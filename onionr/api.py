'''
    Onionr - P2P Microblogging Platform & Social network

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
import flask
from flask import request, Response, abort, send_from_directory
from multiprocessing import Process
from gevent.pywsgi import WSGIServer
import sys, random, threading, hmac, hashlib, base64, time, math, os, json
import core
from onionrblockapi import Block
import onionrutils, onionrexceptions, onionrcrypto, blockimporter, onionrevents as events, logger, config

class API:
    '''
        Main HTTP API (Flask)
    '''

    callbacks = {'public' : {}, 'private' : {}}

    def validateToken(self, token):
        '''
            Validate that the client token matches the given token
        '''
        try:
            if not hmac.compare_digest(self.clientToken, token):
                return False
            else:
                return True
        except TypeError:
            return False

    def guessMime(path):
        '''
            Guesses the mime type from the input filename
        '''

        mimetypes = {
            'html' : 'text/html',
            'js' : 'application/javascript',
            'css' : 'text/css',
            'png' : 'image/png',
            'jpg' : 'image/jpeg'
        }

        for mimetype in mimetypes:
            logger.debug(path + ' endswith .' + mimetype + '?')
            if path.endswith('.%s' % mimetype):
                logger.debug('- True!')
                return mimetypes[mimetype]
            else:
                logger.debug('- no')

        logger.debug('%s not in %s' % (path, mimetypes))
        return 'text/plain'

    def __init__(self, debug, API_VERSION):
        '''
            Initialize the api server, preping variables for later use

            This initilization defines all of the API entry points and handlers for the endpoints and errors
            This also saves the used host (random localhost IP address) to the data folder in host.txt
        '''

        config.reload()

        if config.get('dev_mode', True):
            self._developmentMode = True
            logger.set_level(logger.LEVEL_DEBUG)
        else:
            self._developmentMode = False
            logger.set_level(logger.LEVEL_INFO)

        self.debug = debug
        self._privateDelayTime = 3
        self._core = core.Core()
        self._crypto = onionrcrypto.OnionrCrypto(self._core)
        self._utils = onionrutils.OnionrUtils(self._core)
        app = flask.Flask(__name__)
        bindPort = int(config.get('client.port', 59496))
        self.bindPort = bindPort
        self.clientToken = config.get('client.hmac')
        self.timeBypassToken = base64.b16encode(os.urandom(32)).decode()

        self.i2pEnabled = config.get('i2p.host', False)

        self.mimeType = 'text/plain'
        self.overrideCSP = False

        with open(self._core.dataDir + 'time-bypass.txt', 'w') as bypass:
            bypass.write(self.timeBypassToken)

        if not debug and not self._developmentMode:
            hostOctets = [127, random.randint(0x02, 0xFF), random.randint(0x02, 0xFF), random.randint(0x02, 0xFF)]
            self.host = '.'.join(hostOctets)
        else:
            self.host = '127.0.0.1'

        with open(self._core.dataDir + 'host.txt', 'w') as file:
            file.write(self.host)

        @app.before_request
        def beforeReq():
            '''
                Simply define the request as not having yet failed, before every request.
            '''
            self.requestFailed = False
            return

        @app.after_request
        def afterReq(resp):
            if not self.requestFailed:
                resp.headers['Access-Control-Allow-Origin'] = '*'
            #else:
            #    resp.headers['server'] = 'Onionr'
            resp.headers['Content-Type'] = self.mimeType
            if not self.overrideCSP:
                resp.headers["Content-Security-Policy"] =  "default-src 'none'; script-src 'none'; object-src 'none'; style-src data: 'unsafe-inline'; img-src data:; media-src 'none'; frame-src 'none'; font-src 'none'; connect-src 'none'"
            resp.headers['X-Frame-Options'] = 'deny'
            resp.headers['X-Content-Type-Options'] = "nosniff"
            resp.headers['api'] = API_VERSION

            # reset to text/plain to help prevent browser attacks
            self.mimeType = 'text/plain'
            self.overrideCSP = False

            return resp
            
        @app.route('/www/private/<path:path>')
        def www_private(path):
            startTime = math.floor(time.time())

            if request.args.get('timingToken') is None:
                timingToken = ''
            else:
                timingToken = request.args.get('timingToken')

            if not config.get("www.private.run", True):
                abort(403)

            self.validateHost('private')

            endTime = math.floor(time.time())
            elapsed = endTime - startTime

            if not hmac.compare_digest(timingToken, self.timeBypassToken):
                if elapsed < self._privateDelayTime:
                    time.sleep(self._privateDelayTime - elapsed)

            return send_from_directory('static-data/www/private/', path)

        @app.route('/www/public/<path:path>')
        def www_public(path):
            if not config.get("www.public.run", True):
                abort(403)

            self.validateHost('public')

            return send_from_directory('static-data/www/public/', path)

        @app.route('/ui/<path:path>')
        def ui_private(path):
            startTime = math.floor(time.time())

            '''
            if request.args.get('timingToken') is None:
                timingToken = ''
            else:
                timingToken = request.args.get('timingToken')
            '''

            if not config.get("www.ui.run", True):
                abort(403)

            if config.get("www.ui.private", True):
                self.validateHost('private')
            else:
                self.validateHost('public')

            '''
            endTime = math.floor(time.time())
            elapsed = endTime - startTime

            if not hmac.compare_digest(timingToken, self.timeBypassToken):
                if elapsed < self._privateDelayTime:
                    time.sleep(self._privateDelayTime - elapsed)
            '''

            logger.debug('Serving %s' % path)

            self.mimeType = API.guessMime(path)
            self.overrideCSP = True

            return send_from_directory('static-data/www/ui/dist/', path, mimetype = API.guessMime(path))

        @app.route('/client/')
        def private_handler():
            if request.args.get('timingToken') is None:
                timingToken = ''
            else:
                timingToken = request.args.get('timingToken')
            data = request.args.get('data')
            try:
                data = data
            except:
                data = ''
            startTime = math.floor(time.time())

            action = request.args.get('action')
            #if not self.debug:
            token = request.args.get('token')

            if not self.validateToken(token):
                abort(403)

            events.event('webapi_private', onionr = None, data = {'action' : action, 'data' : data, 'timingToken' : timingToken, 'token' : token})

            self.validateHost('private')
            if action == 'hello':
                resp = Response('Hello, World! ' + request.host)
            elif action == 'shutdown':
                # request.environ.get('werkzeug.server.shutdown')()
                self.http_server.stop()
                resp = Response('Goodbye')
            elif action == 'ping':
                resp = Response('pong')
            elif action == "insertBlock":
                response = {'success' : False, 'reason' : 'An unknown error occurred'}

                if not ((data is None) or (len(str(data).strip()) == 0)):
                    try:
                        decoded = json.loads(data)

                        block = Block()

                        sign = False

                        for key in decoded:
                            val = decoded[key]

                            key = key.lower()

                            if key == 'type':
                                block.setType(val)
                            elif key in ['body', 'content']:
                                block.setContent(val)
                            elif key == 'parent':
                                block.setParent(val)
                            elif key == 'sign':
                                sign = (str(val).lower() == 'true')

                        hash = block.save(sign = sign)

                        if not hash is False:
                            response['success'] = True
                            response['hash'] = hash
                            response['reason'] = 'Successfully wrote block to file'
                        else:
                            response['reason'] = 'Failed to save the block'
                    except Exception as e:
                        logger.warn('insertBlock api request failed', error = e)
                        logger.debug('Here\'s the request: %s' % data)
                else:
                    response = {'success' : False, 'reason' : 'Missing `data` parameter.', 'blocks' : {}}

                resp = Response(json.dumps(response))
            elif action == 'searchBlocks':
                response = {'success' : False, 'reason' : 'An unknown error occurred', 'blocks' : {}}

                if not ((data is None) or (len(str(data).strip()) == 0)):
                    try:
                        decoded = json.loads(data)

                        type = None
                        signer = None
                        signed = None
                        parent = None
                        reverse = False
                        limit = None

                        for key in decoded:
                            val = decoded[key]

                            key = key.lower()

                            if key == 'type':
                                type = str(val)
                            elif key == 'signer':
                                if isinstance(val, list):
                                    signer = val
                                else:
                                    signer = str(val)
                            elif key == 'signed':
                                signed = (str(val).lower() == 'true')
                            elif key == 'parent':
                                parent = str(val)
                            elif key == 'reverse':
                                reverse = (str(val).lower() == 'true')
                            elif key == 'limit':
                                limit = 10000

                                if val is None:
                                    val = limit

                                limit = min(limit, int(val))

                        blockObjects = Block.getBlocks(type = type, signer = signer, signed = signed, parent = parent, reverse = reverse, limit = limit)

                        logger.debug('%s results for query %s' % (len(blockObjects), decoded))

                        blocks = list()

                        for block in blockObjects:
                            blocks.append({
                                'hash' : block.getHash(),
                                'type' : block.getType(),
                                'content' : block.getContent(),
                                'signature' : block.getSignature(),
                                'signedData' : block.getSignedData(),
                                'signed' : block.isSigned(),
                                'valid' : block.isValid(),
                                'date' : (int(block.getDate().strftime("%s")) if not block.getDate() is None else None),
                                'parent' : (block.getParent().getHash() if not block.getParent() is None else None),
                                'metadata' : block.getMetadata(),
                                'header' : block.getHeader()
                            })

                        response['success'] = True
                        response['blocks'] = blocks
                        response['reason'] = 'Success'
                    except Exception as e:
                        logger.warn('searchBlock api request failed', error = e)
                        logger.debug('Here\'s the request: %s' % data)
                else:
                    response = {'success' : False, 'reason' : 'Missing `data` parameter.', 'blocks' : {}}

                resp = Response(json.dumps(response))

            elif action in API.callbacks['private']:
                resp = Response(str(getCallback(action, scope = 'private')(request)))
            else:
                resp = Response('(O_o) Dude what? (invalid command)')
            endTime = math.floor(time.time())
            elapsed = endTime - startTime

            # if bypass token not used, delay response to prevent timing attacks
            if not hmac.compare_digest(timingToken, self.timeBypassToken):
                if elapsed < self._privateDelayTime:
                    time.sleep(self._privateDelayTime - elapsed)

            return resp

        @app.route('/')
        def banner():
            self.mimeType = 'text/html'
            self.validateHost('public')
            try:
                with open('static-data/index.html', 'r') as html:
                    resp = Response(html.read())
            except FileNotFoundError:
                resp = Response("")
            return resp

        @app.route('/public/upload/', methods=['POST'])
        def blockUpload():
            self.validateHost('public')
            resp = 'failure'
            try:
                data = request.form['block']
            except KeyError:
                logger.warn('No block specified for upload')
                pass
            else:
                if sys.getsizeof(data) < 100000000:
                    try:
                        if blockimporter.importBlockFromData(data, self._core):
                            resp = 'success'
                        else:
                            logger.warn('Error encountered importing uploaded block')
                    except onionrexceptions.BlacklistedBlock:
                        logger.debug('uploaded block is blacklisted')
                        pass

            resp = Response(resp)
            return resp

        @app.route('/public/announce/', methods=['POST'])
        def acceptAnnounce():
            self.validateHost('public')
            resp = 'failure'
            powHash = ''
            randomData = ''
            newNode = ''
            ourAdder = self._core.hsAddress.encode()
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
                    nodes = newNode + self._core.hsAddress.encode()
                    nodes = self._core._crypto.blake2bHash(nodes)
                    powHash = self._core._crypto.blake2bHash(randomData + nodes)
                    try:
                        powHash = powHash.decode()
                    except AttributeError:
                        pass
                    if powHash.startswith('0000'):
                        try:
                            newNode = newNode.decode()
                        except AttributeError:
                            pass
                        if self._core.addAddress(newNode):
                            resp = 'Success'
                    else:
                        logger.warn(newNode.decode() + ' failed to meet POW: ' + powHash)
            resp = Response(resp)
            return resp   

        @app.route('/public/')
        def public_handler():
            # Public means it is publicly network accessible
            self.validateHost('public')
            action = request.args.get('action')
            requestingPeer = request.args.get('myID')
            data = request.args.get('data')
            try:
                data = data
            except:
                data = ''

            events.event('webapi_public', onionr = None, data = {'action' : action, 'data' : data, 'requestingPeer' : requestingPeer, 'request' : request})

            if action == 'firstConnect':
                pass
            elif action == 'ping':
                resp = Response("pong!")
            elif action == 'getSymmetric':
                resp = Response(self._crypto.generateSymmetric())
            elif action == 'getDBHash':
                resp = Response(self._utils.getBlockDBHash())
            elif action == 'getBlockHashes':
                resp = Response('\n'.join(self._core.getBlockList()))
            # setData should be something the communicator initiates, not this api
            elif action == 'getData':
                resp = ''
                if self._utils.validateHash(data):
                    if os.path.exists(self._core.dataDir + 'blocks/' + data + '.dat'):
                        block = Block(hash=data.encode(), core=self._core)
                        resp = base64.b64encode(block.getRaw().encode()).decode()
                if len(resp) == 0:
                    abort(404)
                    resp = ""
                resp = Response(resp)
            elif action == 'pex':
                response = ','.join(self._core.listAdders())
                if len(response) == 0:
                    response = 'none'
                resp = Response(response)
            elif action == 'kex':
                peers = self._core.listPeers(getPow=True)
                response = ','.join(peers)
                resp = Response(response)
            elif action in API.callbacks['public']:
                resp = Response(str(getCallback(action, scope = 'public')(request)))
            else:
                resp = Response("")

            return resp

        @app.errorhandler(404)
        def notfound(err):
            self.requestFailed = True
            resp = Response("")

            return resp

        @app.errorhandler(403)
        def authFail(err):
            self.requestFailed = True
            resp = Response("403")
            return resp

        @app.errorhandler(401)
        def clientError(err):
            self.requestFailed = True
            resp = Response("Invalid request")

            return resp
        if not os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            logger.info('Starting client on ' + self.host + ':' + str(bindPort) + '...', timestamp=False)

        try:
            while len(self._core.hsAddress) == 0:
                self._core.refreshFirstStartVars()
                time.sleep(0.5)
            self.http_server = WSGIServer((self.host, bindPort), app, log=None)
            self.http_server.serve_forever()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            logger.error(str(e))
            logger.fatal('Failed to start client on ' + self.host + ':' + str(bindPort) + ', exiting...')
            exit(1)

    def validateHost(self, hostType):
        '''
            Validate various features of the request including:

            If private (/client/), is the host header local?
            If public (/public/), is the host header onion or i2p?

            Was X-Request-With used?
        '''
        if self.debug:
            return
        # Validate host header, to protect against DNS rebinding attacks
        host = self.host
        if hostType == 'private':
            if not request.host.startswith('127') and not self._utils.checkIsIP(request.host):
                abort(403)
        elif hostType == 'public':
            if not request.host.endswith('onion') and not request.host.endswith('i2p'):
                abort(403)
        # Validate x-requested-with, to protect against CSRF/metadata leaks

        if not self.i2pEnabled and request.host.endswith('i2p'):
            abort(403)

        if not self._developmentMode:
            try:
                request.headers['X-Requested-With']
            except:
                # we exit rather than abort to avoid fingerprinting
                logger.debug('Avoiding fingerprinting, exiting...')
                sys.exit(1)

    def setCallback(action, callback, scope = 'public'):
        if not scope in API.callbacks:
            return False

        API.callbacks[scope][action] = callback

        return True

    def removeCallback(action, scope = 'public'):
        if (not scope in API.callbacks) or (not action in API.callbacks[scope]):
            return False

        del API.callbacks[scope][action]

        return True

    def getCallback(action, scope = 'public'):
        if (not scope in API.callbacks) or (not action in API.callbacks[scope]):
            return None

        return API.callbacks[scope][action]

    def getCallbacks(scope = None):
        if (not scope is None) and (scope in API.callbacks):
            return API.callbacks[scope]

        return API.callbacks
