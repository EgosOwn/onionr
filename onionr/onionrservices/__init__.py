import stem
import core
from . import connectionserver, connectionclient, bootstrapservice
class OnionrServices:
    def __init__(self, onionr_core):
        assert isinstance(onionr_core, core.Core)
        self._core = onionr_core
        self.servers = {}
        self.clients = {}
        return
    
    def create_server(self):
        return
    
    def create_client(self, peer):
        # Create ephemeral onion service to bootstrap connection
        address = bootstrapservice.bootstrap_client_service(peer)
        return address