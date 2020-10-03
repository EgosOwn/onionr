from onionrutils.stringvalidators import validate_transport
from coredb.keydb.addkeys import add_address
from coredb.keydb.listkeys import list_adders


def add_peer(peer):
    # this is ok for security since add_address does this manually
    assert validate_transport(peer)
    if peer in list_adders():
        return "already added"
    if add_address(peer):
        return "success"
    else:
        return "failure, invalid address"
