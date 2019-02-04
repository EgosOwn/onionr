'''
    Onionr - P2P Anonymous Storage Network

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
from gevent.pywsgi import WSGIServer, WSGIHandler
from gevent import Timeout
import flask, cgi
from flask import request, Response, abort, send_from_directory
import sys, random, threading, hmac, hashlib, base64, time, math, os, json, socket
import core
from onionrblockapi import Block
import onionrutils, onionrexceptions, onionrcrypto, blockimporter, onionrevents as events, logger, config, onionr

class FDSafeHandler(WSGIHandler):
    def handle(self):
       timeout = Timeout(60, exception=Exception)
       timeout.start()

       #timeout = gevent.Timeout.start_new(3)
       try:
           WSGIHandler.handle(self)
       except Timeout as ex:
           raise

def guessMime(path):
    '''
        Guesses the mime type of a file from the input filename
    '''
    mimetypes = {
        'html' : 'text/html',
        'js' : 'application/javascript',
        'css' : 'text/css',
        'png' : 'image/png',
        'jpg' : 'image/jpeg'
    }

    for mimetype in mimetypes:
        if path.endswith('.%s' % mimetype):
            return mimetypes[mimetype]

    return 'text/plain'

def setBindIP(filePath):
    '''Set a random localhost IP to a specified file (intended for private or public API localhost IPs)'''
    hostOctets = [str(127), str(random.randint(0x02, 0xFF)), str(random.randint(0x02, 0xFF)), str(random.randint(0x02, 0xFF))]
    data = '.'.join(hostOctets)
    
    # Try to bind IP. Some platforms like Mac block non normal 127.x.x.x
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((data, 0))
    except OSError:
        logger.warn('Your platform appears to not support random local host addresses 127.x.x.x. Falling back to 127.0.0.1.')
        data = '127.0.0.1'
    s.close()
    
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
        logger.info('Running public api on %s:%s' % (self.host, self.bindPort))

        @app.before_request
        def validateRequest():
            '''Validate request has the correct hostname'''
            # If high security level, deny requests to public
            if config.get('general.security_level', default=0) > 0:
                abort(403)
            if type(self.torAdder) is None and type(self.i2pAdder) is None:
                # abort if our hs addresses are not known
                abort(403)
            if request.host not in (self.i2pAdder, self.torAdder):
                abort(403)

        @app.after_request
        def sendHeaders(resp):
            '''Send api, access control headers'''
            resp.headers['Date'] = 'Thu, 1 Jan 1970 00:00:00 GMT' # Clock info is probably useful to attackers. Set to unix epoch.
            resp.headers["Content-Security-Policy"] =  "default-src 'none'; script-src 'none'; object-src 'none'; style-src data: 'unsafe-inline'; img-src data:; media-src 'none'; frame-src 'none'; font-src 'none'; connect-src 'none'"
            resp.headers['X-Frame-Options'] = 'deny'
            resp.headers['X-Content-Type-Options'] = "nosniff"
            resp.headers['X-API'] = onionr.API_VERSION
            resp.headers['Connection'] = "close"
            return resp

        @app.route('/')
        def banner():
            try:
                with open('static-data/index.html', 'r') as html:
                    resp = Response(html.read(), mimetype='text/html')
            except FileNotFoundError:
                resp = Response("")
            return resp

        @app.route('/getblocklist')
        def getBlockList():
            dateAdjust = request.args.get('date')
            bList = clientAPI._core.getBlockList(dateRec=dateAdjust)
            for b in self.hideBlocks:
                if b in bList:
                    bList.remove(b)
            return Response('\n'.join(bList))

        @app.route('/getdata/<name>')
        def getBlockData(name):
            resp = ''
            data = name
            if clientAPI._utils.validateHash(data):
                if data not in self.hideBlocks:
                    if data in clientAPI._core.getBlockList():
                        block = clientAPI.getBlockData(data, raw=True).encode()
                        resp = base64.b64encode(block).decode()
            if len(resp) == 0:
                abort(404)
                resp = ""
            return Response(resp)

        @app.route('/www/<path:path>')
        def wwwPublic(path):
            if not config.get("www.public.run", True):
                abort(403)
            return send_from_directory(config.get('www.public.path', 'static-data/www/public/'), path)

        @app.route('/ping')
        def ping():
            return Response("pong!")

        @app.route('/getdbhash')
        def getDBHash():
            return Response(clientAPI._utils.getBlockDBHash())

        @app.route('/pex')
        def peerExchange():
            response = ','.join(clientAPI._core.listAdders(recent=3600))
            if len(response) == 0:
                response = ''
            return Response(response)
        
        @app.route('/announce', methods=['post'])
        def acceptAnnounce():
            resp = 'failure'
            powHash = ''
            randomData = ''
            newNode = ''
            ourAdder = clientAPI._core.hsAddress.encode()
            try:
                newNode = request.form['node'].encode()
            except KeyError:
                logger.warn('No block specified for upload')
                pass
            else:
                try:
                    randomData = request.form['random']
                    randomData = base64.b64decode(randomData)
                except KeyError:
                    logger.warn('No random data specified for upload')
                else:
                    nodes = newNode + clientAPI._core.hsAddress.encode()
                    nodes = clientAPI._core._crypto.blake2bHash(nodes)
                    powHash = clientAPI._core._crypto.blake2bHash(randomData + nodes)
                    try:
                        powHash = powHash.decode()
                    except AttributeError:
                        pass
                    if powHash.startswith('0000'):
                        try:
                            newNode = newNode.decode()
                        except AttributeError:
                            pass
                        if clientAPI._core.addAddress(newNode):
                            resp = 'Success'
                    else:
                        logger.warn(newNode.decode() + ' failed to meet POW: ' + powHash)
            resp = Response(resp)
            return resp

        @app.route('/upload', methods=['post'])
        def upload():
            resp = 'failure'
            try:
                data = request.form['block']
            except KeyError:
                logger.warn('No block specified for upload')
                pass
            else:
                if sys.getsizeof(data) < 100000000:
                    try:
                        if blockimporter.importBlockFromData(data, clientAPI._core):
                            resp = 'success'
                        else:
                            logger.warn('Error encountered importing uploaded block')
                    except onionrexceptions.BlacklistedBlock:
                        logger.debug('uploaded block is blacklisted')
                        pass
            if resp == 'failure':
                abort(400)
            resp = Response(resp)
            return resp

        clientAPI.setPublicAPIInstance(self)
        while self.torAdder == '':
            clientAPI._core.refreshFirstStartVars()
            self.torAdder = clientAPI._core.hsAddress
            time.sleep(1)
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

            This initilization defines all of the API entry points and handlers for the endpoints and errors
            This also saves the used host (random localhost IP address) to the data folder in host.txt
        '''
        # assert isinstance(onionrInst, onionr.Onionr)
        # configure logger and stuff
        onionr.Onionr.setupConfig('data/', self = self)

        self.debug = debug
        self._privateDelayTime = 3
        self._core = onionrInst.onionrCore
        self.startTime = self._core._utils.getEpoch()
        self._crypto = onionrcrypto.OnionrCrypto(self._core)
        self._utils = onionrutils.OnionrUtils(self._core)
        app = flask.Flask(__name__)
        bindPort = int(config.get('client.client.port', 59496))
        self.bindPort = bindPort

        # Be extremely mindful of this
        self.whitelistEndpoints = ('site', 'www', 'onionrhome', 'board', 'boardContent', 'sharedContent', 'mail', 'mailindex')

        self.clientToken = config.get('client.webpassword')
        self.timeBypassToken = base64.b16encode(os.urandom(32)).decode()

        self.publicAPI = None # gets set when the thread calls our setter... bad hack but kinda necessary with flask
        #threading.Thread(target=PublicAPI, args=(self,)).start()
        self.host = setBindIP(self._core.privateApiHostFile)
        logger.info('Running api on %s:%s' % (self.host, self.bindPort))
        self.httpServer = ''

        self.queueResponse = {}
        onionrInst.setClientAPIInst(self)

        @app.before_request
        def validateRequest():
            '''Validate request has set password and is the correct hostname'''
            if request.host != '%s:%s' % (self.host, self.bindPort):
                abort(403)
            if request.endpoint in self.whitelistEndpoints:
                return
            try:
                if not hmac.compare_digest(request.headers['token'], self.clientToken):
                    abort(403)
            except KeyError:
                abort(403)

        @app.after_request
        def afterReq(resp):
            #resp.headers["Content-Security-Policy"] =  "default-src 'none'; script-src 'none'; object-src 'none'; style-src data: 'unsafe-inline'; img-src data:; media-src 'none'; frame-src 'none'; font-src 'none'; connect-src 'none'"
            resp.headers['Content-Security-Policy'] = "default-src 'none'; script-src 'self'; object-src 'none'; style-src 'self'; img-src 'self'; media-src 'none'; frame-src 'none'; font-src 'none'; connect-src 'self'"
            resp.headers['X-Frame-Options'] = 'deny'
            resp.headers['X-Content-Type-Options'] = "nosniff"
            resp.headers['X-API'] = onionr.API_VERSION
            resp.headers['Server'] = ''
            resp.headers['Date'] = 'Thu, 1 Jan 1970 00:00:00 GMT' # Clock info is probably useful to attackers. Set to unix epoch.
            resp.headers['Connection'] = "close"
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

        @app.route('/board/<path:path>', endpoint='boardContent')
        def boardContent(path):
            return send_from_directory('static-data/www/board/', path)
        @app.route('/shared/<path:path>', endpoint='sharedContent')
        def sharedContent(path):
            return send_from_directory('static-data/www/shared/', path)

        @app.route('/www/<path:path>', endpoint='www')
        def wwwPublic(path):
            if not config.get("www.private.run", True):
                abort(403)
            return send_from_directory(config.get('www.private.path', 'static-data/www/private/'), path)

        @app.route('/queueResponseAdd/<name>', methods=['post'])
        def queueResponseAdd(name):
            self.queueResponse[name] = request.form['data']
            return Response('success')
        
        @app.route('/queueResponse/<name>')
        def queueResponse(name):
            resp = 'failure'
            try:
                resp = self.queueResponse[name]
            except KeyError:
                pass
            else:
                del self.queueResponse[name]
            return Response(resp)
            
        @app.route('/ping')
        def ping():
            return Response("pong!")

        @app.route('/', endpoint='onionrhome')
        def hello():
            return send_from_directory('static-data/www/private/', 'index.html')
        
        @app.route('/getblocksbytype/<name>')
        def getBlocksByType(name):
            blocks = self._core.getBlocksByType(name)
            return Response(','.join(blocks))
        
        @app.route('/getblockbody/<name>')
        def getBlockBodyData(name):
            resp = ''
            if self._core._utils.validateHash(name):
                try:
                    resp = Block(name, decrypt=True).bcontent
                    #resp =  cgi.escape(Block(name, decrypt=True).bcontent, quote=True)
                except TypeError:
                    pass
            else:
                abort(404)
            return Response(resp)
        
        @app.route('/getblockdata/<name>')
        def getData(name):
            resp = ""
            if self._core._utils.validateHash(name):
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

        @app.route('/site/<name>', endpoint='site')
        def site(name):
            bHash = name
            resp = 'Not Found'
            if self._core._utils.validateHash(bHash):
                try:
                    resp = Block(bHash).bcontent
                except TypeError:
                    pass
                try:
                    resp = base64.b64decode(resp)
                except:
                    pass
            if resp == 'Not Found':
                abourt(404)
            return Response(resp)

        @app.route('/waitforshare/<name>', methods=['post'])
        def waitforshare():
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
            return Response(self._core._utils.getHumanReadableID(name))

        self.httpServer = WSGIServer((self.host, bindPort), app, log=None, handler_class=FDSafeHandler)
        self.httpServer.serve_forever()

    def setPublicAPIInstance(self, inst):
        assert isinstance(inst, PublicAPI)
        self.publicAPI = inst

    def validateToken(self, token):
        '''
            Validate that the client token matches the given token
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
                return self._utils.getEpoch - startTime
            except AttributeError:
                # Don't error on race condition with startup
                pass
    
    def getBlockData(self, bHash, decrypt=False, raw=False, headerOnly=False):
        assert self._core._utils.validateHash(bHash)
        bl = Block(bHash, core=self._core)
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
                bl.bheader['meta'] = ''
                retData = {'meta': bl.bheader, 'metadata': bl.bmetadata}
            return json.dumps(retData)
        else:
            return bl.raw
