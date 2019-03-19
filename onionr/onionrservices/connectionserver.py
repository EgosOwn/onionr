import stem, flask
import core
class ConnectionServer:
    def __init__(self, peer, address, core_inst=None):
        if core_inst is None:
            self.core_inst = core.Core()
        else:
            self.core_inst = core_inst

        if not core_inst._utils.validatePubKey(peer):
            raise ValueError('Peer must be valid base32 ed25519 public key')
        
        service_app = flask.Flask(__name__)
        service_port = getOpenPort()
        http_server = WSGIServer(('127.0.0.1', service_port), service_app, log=None)
        
        @service_app.route('/ping')
        def get_ping():
            return "pong!"

        with Controller.from_port(port=core_inst.config.get('tor.controlPort')) as controller:
            # Connect to the Tor process for Onionr
            controller.authenticate(core_inst.config.get('tor.controlpassword'))
            # Create the v3 onion service
            response = controller.create_ephemeral_hidden_service({80: service_port}, await_publication = True, key_type='ED25519-V3')
            logger.info('hosting on ' + response.service_id)
            http_server.serve_forever()