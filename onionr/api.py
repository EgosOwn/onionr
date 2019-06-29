'''
    Onionr - Private P2P Communication

    This file handles all incoming http requests to the client, using Flask
'''
'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import random, threading, hmac, base64, time, os, json, socket
from gevent.pywsgi import WSGIServer, WSGIHandler
from gevent import Timeout
import flask
from flask import request, Response, abort, send_from_directory
import core
import onionrexceptions, onionrcrypto, blockimporter, onionrevents as events, logger, config, onionrblockapi
import httpapi
from httpapi import friendsapi, profilesapi, configapi, miscpublicapi
from onionrservices import httpheaders
import onionr
from onionrutils import bytesconverter, stringvalidators, epoch, mnemonickeys

config.reload()
class FDSafeHandler(WSGIHandler):
    '''Our WSGI handler. Doesn't do much non-default except timeouts'''
    def __init__(self, sock, address, server, rfile=None):
        self.socket =  sock
        self.address = address
        self.server = server
        self.rfile = rfile
    def handle(self):
        while True:
            timeout = Timeout(120, exception=Exception)
            try:
                FDSafeHandler.handle(self)
                timeout.start()
            except Timeout as ex:
                raise

def setBindIP(filePath=''):
    '''Set a random localhost IP to a specified file (intended for private or public API localhost IPs)'''
    if config.get('general.random_bind_ip', True):
        hostOctets = [str(127), str(random.randint(0x02, 0xFF)), str(random.randint(0x02, 0xFF)), str(random.randint(0x02, 0xFF))]
        data = '.'.join(hostOctets)
        # Try to bind IP. Some platforms like Mac block non normal 127.x.x.x
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((data, 0))
        except OSError:
            # if mac/non-bindable, show warning and default to 127.0.0.1
            logger.warn('Your platform appears to not support random local host addresses 127.x.x.x. Falling back to 127.0.0.1.')
            data = '127.0.0.1'
        s.close()
    else:
        data = '127.0.0.1'
    if filePath != '':
        with open(filePath, 'w') as bindFile:
            bindFile.write(data)
    return data

class PublicAPI:
    '''
        The new client api server, isolated from the public api
    '''
    def __init__(self, clientAPI):
        assert isinstance(clientAPI, API)
        app = flask.Flask('PublicAPI')
        self.i2pEnabled = config.get('i2p.host', False)
        self.hideBlocks = [] # Blocks to be denied sharing
        self.host = setBindIP(clientAPI._core.publicApiHostFile)
        self.torAdder = clientAPI._core.hsAddress
        self.i2pAdder = clientAPI._core.i2pAddress
        self.bindPort = config.get('client.public.port')
        self.lastRequest = 0
        self.hitCount = 0 # total rec requests to public api since server started
        logger.info('Running public api on %s:%s' % (self.host, self.bindPort))

        @app.before_request
        def validateRequest():
            '''Validate request has the correct hostname'''
            # If high security level, deny requests to public (HS should be disabled anyway for Tor, but might not be for I2P)
            if config.get('general.security_level', default=1) > 0:
                abort(403)
            if type(self.torAdder) is None and type(self.i2pAdder) is None:
                # abort if our hs addresses are not known
                abort(403)
            if request.host not in (self.i2pAdder, self.torAdder):
                # Disallow connection if wrong HTTP hostname, in order to prevent DNS rebinding attacks
                abort(403)
            self.hitCount += 1 # raise hit count for valid requests

        @app.after_request
        def sendHeaders(resp):
            '''Send api, access control headers'''
            resp = httpheaders.set_default_onionr_http_headers(resp)
            # Network API version
            resp.headers['X-API'] = onionr.API_VERSION
            self.lastRequest = epoch.get_rounded_epoch(roundS=5)
            return resp

        @app.route('/')
        def banner():
            # Display a bit of information to people who visit a node address in their browser
            try:
                with open('static-data/index.html', 'r') as html:
                    resp = Response(html.read(), mimetype='text/html')
            except FileNotFoundError:
                resp = Response("")
            return resp

        @app.route('/getblocklist')
        def getBlockList():
            return httpapi.miscpublicapi.public_block_list(clientAPI, self, request)

        @app.route('/getdata/<name>')
        def getBlockData(name):
            # Share data for a block if we have it
            return httpapi.miscpublicapi.public_get_block_data(clientAPI, self, name)

        @app.route('/www/<path:path>')
        def wwwPublic(path):
            # A way to share files directly over your .onion
            if not config.get("www.public.run", True):
                abort(403)
            return send_from_directory(config.get('www.public.path', 'static-data/www/public/'), path)

        @app.route('/ping')
        def ping():
            # Endpoint to test if nodes are up
            return Response("pong!")

        @app.route('/pex')
        def peerExchange():
            response = ','.join(clientAPI._core.listAdders(recent=3600))
            if len(response) == 0:
                response = ''
            return Response(response)
        
        @app.route('/announce', methods=['post'])
        def acceptAnnounce():
            resp = httpapi.miscpublicapi.announce(clientAPI, request)
            return resp

        @app.route('/upload', methods=['post'])
        def upload():
            '''Accept file uploads. In the future this will be done more often than on creation 
            to speed up block sync
            '''
            return httpapi.miscpublicapi.upload(clientAPI, request)

        # Set instances, then startup our public api server
        clientAPI.setPublicAPIInstance(self)
        while self.torAdder == '':
            clientAPI._core.refreshFirstStartVars()
            self.torAdder = clientAPI._core.hsAddress
            time.sleep(0.1)
        self.httpServer = WSGIServer((self.host, self.bindPort), app, log=None, handler_class=FDSafeHandler)
        self.httpServer.serve_forever()

class API:
    '''
        Client HTTP api
    '''

    callbacks = {'public' : {}, 'private' : {}}

    def __init__(self, onionrInst, debug, API_VERSION):
        '''
            Initialize the api server, preping variables for later use

            This initialization defines all of the API entry points and handlers for the endpoints and errors
            This also saves the used host (random localhost IP address) to the data folder in host.txt
        '''

        self.debug = debug
        self._core = onionrInst.onionrCore
        self.startTime = epoch.get_epoch()
        self._crypto = onionrcrypto.OnionrCrypto(self._core)
        app = flask.Flask(__name__)
        bindPort = int(config.get('client.client.port', 59496))
        self.bindPort = bindPort

        # Be extremely mindful of this. These are endpoints available without a password
        self.whitelistEndpoints = ('site', 'www', 'onionrhome', 'homedata', 'board', 'profiles', 'profilesindex', 
        'boardContent', 'sharedContent', 'mail', 'mailindex', 'friends', 'friendsindex',
        'clandestine', 'clandestineIndex')

        self.clientToken = config.get('client.webpassword')
        self.timeBypassToken = base64.b16encode(os.urandom(32)).decode()

        self.publicAPI = None # gets set when the thread calls our setter... bad hack but kinda necessary with flask
        #threading.Thread(target=PublicAPI, args=(self,)).start()
        self.host = setBindIP(self._core.privateApiHostFile)
        logger.info('Running api on %s:%s' % (self.host, self.bindPort))
        self.httpServer = ''

        self.queueResponse = {}
        onionrInst.setClientAPIInst(self)
        app.register_blueprint(friendsapi.friends)
        app.register_blueprint(profilesapi.profile_BP)
        app.register_blueprint(configapi.config_BP)
        httpapi.load_plugin_blueprints(app)

        @app.before_request
        def validateRequest():
            '''Validate request has set password and is the correct hostname'''
            # For the purpose of preventing DNS rebinding attacks
            if request.host != '%s:%s' % (self.host, self.bindPort):
                abort(403)
            if request.endpoint in self.whitelistEndpoints:
                return
            try:
                if not hmac.compare_digest(request.headers['token'], self.clientToken):
                    if not hmac.compare_digest(request.form['token'], self.clientToken):
                        abort(403)
            except KeyError:
                if not hmac.compare_digest(request.form['token'], self.clientToken):
                    abort(403)

        @app.after_request
        def afterReq(resp):
            # Security headers
            resp = httpheaders.set_default_onionr_http_headers(resp)
            if request.endpoint == 'site':
                resp.headers['Content-Security-Policy'] = "default-src 'none'; style-src data: 'unsafe-inline'; img-src data:"
            else:
                resp.headers['Content-Security-Policy'] = "default-src 'none'; script-src 'self'; object-src 'none'; style-src 'self'; img-src 'self'; media-src 'none'; frame-src 'none'; font-src 'none'; connect-src 'self'"
            return resp

        @app.route('/board/', endpoint='board')
        def loadBoard():
            return send_from_directory('static-data/www/board/', "index.html")

        @app.route('/mail/<path:path>', endpoint='mail')
        def loadMail(path):
            return send_from_directory('static-data/www/mail/', path)
        @app.route('/mail/', endpoint='mailindex')
        def loadMailIndex():
            return send_from_directory('static-data/www/mail/', 'index.html')

        @app.route('/clandestine/<path:path>', endpoint='clandestine')
        def loadClandestine(path):
            return send_from_directory('static-data/www/clandestine/', path)
        @app.route('/clandestine/', endpoint='clandestineIndex')
        def loadClandestineIndex():
            return send_from_directory('static-data/www/clandestine/', 'index.html')
        
        @app.route('/friends/<path:path>', endpoint='friends')
        def loadContacts(path):
            return send_from_directory('static-data/www/friends/', path)

        @app.route('/friends/', endpoint='friendsindex')
        def loadContacts():
            return send_from_directory('static-data/www/friends/', 'index.html')

        @app.route('/profiles/<path:path>', endpoint='profiles')
        def loadContacts(path):
            return send_from_directory('static-data/www/profiles/', path)

        @app.route('/profiles/', endpoint='profilesindex')
        def loadContacts():
            return send_from_directory('static-data/www/profiles/', 'index.html')
        
        @app.route('/serviceactive/<pubkey>')
        def serviceActive(pubkey):
            try:
                if pubkey in self._core.onionrInst.communicatorInst.active_services:
                    return Response('true')
            except AttributeError as e:
                pass
            return Response('false')

        @app.route('/board/<path:path>', endpoint='boardContent')
        def boardContent(path):
            return send_from_directory('static-data/www/board/', path)
        @app.route('/shared/<path:path>', endpoint='sharedContent')
        def sharedContent(path):
            return send_from_directory('static-data/www/shared/', path)

        @app.route('/', endpoint='onionrhome')
        def hello():
            # ui home
            return send_from_directory('static-data/www/private/', 'index.html')
        
        @app.route('/private/<path:path>', endpoint='homedata')
        def homedata(path):
            return send_from_directory('static-data/www/private/', path)

        @app.route('/www/<path:path>', endpoint='www')
        def wwwPublic(path):
            if not config.get("www.private.run", True):
                abort(403)
            return send_from_directory(config.get('www.private.path', 'static-data/www/private/'), path)

        @app.route('/hitcount')
        def get_hit_count():
            return Response(str(self.publicAPI.hitCount))

        @app.route('/queueResponseAdd/<name>', methods=['post'])
        def queueResponseAdd(name):
            # Responses from the daemon. TODO: change to direct var access instead of http endpoint
            self.queueResponse[name] = request.form['data']
            return Response('success')
        
        @app.route('/queueResponse/<name>')
        def queueResponse(name):
            # Fetch a daemon queue response
            resp = 'failure'
            try:
                resp = self.queueResponse[name]
            except KeyError:
                pass
            else:
                del self.queueResponse[name]
            if resp == 'failure':
                return resp, 404
            else:
                return resp
            
        @app.route('/ping')
        def ping():
            # Used to check if client api is working
            return Response("pong!")
        
        @app.route('/getblocksbytype/<name>')
        def getBlocksByType(name):
            blocks = self._core.getBlocksByType(name)
            return Response(','.join(blocks))
        
        @app.route('/getblockbody/<name>')
        def getBlockBodyData(name):
            resp = ''
            if stringvalidators.validate_hash(name):
                try:
                    resp = onionrblockapi.Block(name, decrypt=True).bcontent
                except TypeError:
                    pass
            else:
                abort(404)
            return Response(resp)
        
        @app.route('/getblockdata/<name>')
        def getData(name):
            resp = ""
            if stringvalidators.validate_hash(name):
                if name in self._core.getBlockList():
                    try:
                        resp = self.getBlockData(name, decrypt=True)
                    except ValueError:
                        pass
                else:
                    abort(404)
            else:
                abort(404)
            return Response(resp)

        @app.route('/getblockheader/<name>')
        def getBlockHeader(name):
            resp = self.getBlockData(name, decrypt=True, headerOnly=True)
            return Response(resp)

        @app.route('/lastconnect')
        def lastConnect():
            return Response(str(self.publicAPI.lastRequest))

        @app.route('/site/<name>', endpoint='site')
        def site(name):
            bHash = name
            resp = 'Not Found'
            if stringvalidators.validate_hash(bHash):
                try:
                    resp = onionrblockapi.Block(bHash).bcontent
                except onionrexceptions.NoDataAvailable:
                    abort(404)
                except TypeError:
                    pass
                try:
                    resp = base64.b64decode(resp)
                except:
                    pass
            if resp == 'Not Found' or not resp:
                abort(404)
            return Response(resp)

        @app.route('/waitforshare/<name>', methods=['post'])
        def waitforshare(name):
            '''Used to prevent the **public** api from sharing blocks we just created'''
            assert name.isalnum()
            if name in self.publicAPI.hideBlocks:
                self.publicAPI.hideBlocks.remove(name)
                return Response("removed")
            else:
                self.publicAPI.hideBlocks.append(name)
                return Response("added")

        @app.route('/shutdown')
        def shutdown():
            try:
                self.publicAPI.httpServer.stop()
                self.httpServer.stop()
            except AttributeError:
                pass
            return Response("bye")

        @app.route('/shutdownclean')
        def shutdownClean():
            # good for calling from other clients
            self._core.daemonQueueAdd('shutdown')
            return Response("bye")
        
        @app.route('/getstats')
        def getStats():
            # returns node stats
            #return Response("disabled")
            while True:
                try:    
                    return Response(self._core.serializer.getStats())
                except AttributeError:
                    pass
        
        @app.route('/getuptime')
        def showUptime():
            return Response(str(self.getUptime()))
        
        @app.route('/getActivePubkey')
        def getActivePubkey():
            return Response(self._core._crypto.pubKey)

        @app.route('/getHumanReadable/<name>')
        def getHumanReadable(name):
            return Response(mnemonickeys.get_human_readable_ID(name))

        @app.route('/insertblock', methods=['POST'])
        def insertBlock():
            encrypt = False
            bData = request.get_json(force=True)
            message = bData['message']

            # Detect if message (block body) is not specified
            if type(message) is None:
                return 'failure', 406

            subject = 'temp'
            encryptType = ''
            sign = True
            meta = {}
            to = ''
            try:
                if bData['encrypt']:
                    to = bData['to']
                    encrypt = True
                    encryptType = 'asym'
            except KeyError:
                pass
            try:
                if not bData['sign']:
                    sign = False
            except KeyError:
                pass
            try:
                bType = bData['type']
            except KeyError:
                bType = 'bin'
            try:
                meta = json.loads(bData['meta'])
            except KeyError:
                pass
            threading.Thread(target=self._core.insertBlock, args=(message,), kwargs={'header': bType, 'encryptType': encryptType, 'sign':sign, 'asymPeer': to, 'meta': meta}).start()
            return Response('success')

        self.httpServer = WSGIServer((self.host, bindPort), app, log=None, handler_class=FDSafeHandler)
        self.httpServer.serve_forever()

    def setPublicAPIInstance(self, inst):
        assert isinstance(inst, PublicAPI)
        self.publicAPI = inst

    def validateToken(self, token):
        '''
            Validate that the client token matches the given token. Used to prevent CSRF and data exfiltration
        '''
        if len(self.clientToken) == 0:
            logger.error("client password needs to be set")
            return False
        try:
            if not hmac.compare_digest(self.clientToken, token):
                return False
            else:
                return True
        except TypeError:
            return False

    def getUptime(self):
        while True:
            try:
                return epoch.get_epoch() - self.startTime
            except (AttributeError, NameError):
                # Don't error on race condition with startup
                pass
    
    def getBlockData(self, bHash, decrypt=False, raw=False, headerOnly=False):
        assert stringvalidators.validate_hash(bHash)
        bl = onionrblockapi.Block(bHash, core=self._core)
        if decrypt:
            bl.decrypt()
            if bl.isEncrypted and not bl.decrypted:
                raise ValueError

        if not raw:
            if not headerOnly:
                retData = {'meta':bl.bheader, 'metadata': bl.bmetadata, 'content': bl.bcontent}
                for x in list(retData.keys()):
                    try:
                        retData[x] = retData[x].decode()
                    except AttributeError:
                        pass
            else:
                validSig = False
                signer = bytesconverter.bytes_to_str(bl.signer)
                if bl.isSigned() and stringvalidators.validate_pub_key(signer) and bl.isSigner(signer):
                    validSig = True                    
                bl.bheader['validSig'] = validSig
                bl.bheader['meta'] = ''
                retData = {'meta': bl.bheader, 'metadata': bl.bmetadata}
            return json.dumps(retData)
        else:
            return bl.raw
