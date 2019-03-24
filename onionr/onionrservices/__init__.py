import time
import stem
import core
from . import connectionserver, bootstrapservice

class OnionrServices:
    def __init__(self, onionr_core):
        assert isinstance(onionr_core, core.Core)
        self._core = onionr_core
        self.servers = {}
        self.clients = {}
        self.shutdown = False
        return
    
    def create_server(self, peer, address):
        assert self._core._utils.validateID(address)
        BOOTSTRAP_TRIES = 10
        TRY_WAIT = 3
        for x in range(BOOTSTRAP_TRIES):
            if self._core._utils.doGetRequest('http://' + address + '/ping', port=self._core.config.get('tor.socksport')) == 'pong!':
                connectionserver.ConnectionServer(peer, address, core_inst=self._core)
            else:
                time.sleep(TRY_WAIT)
        else:
            return False

    def create_client(self, peer):
        # Create ephemeral onion service to bootstrap connection
        address = bootstrapservice.bootstrap_client_service(peer)
        return address