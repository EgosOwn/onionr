import communicator, onionrblockapi
def service_creator(daemon):
    assert isinstance(daemon, communicator.OnionrCommunicatorDaemon)
    core = daemon._core
    utils = core._utils
    
    # Find socket connection blocks
    con_blocks = core.getBlocksByType('con')
    for b in con_blocks:
        if not b in daemon.active_services:
            bl = onionrblockapi.Block(b, core=core, decrypt=True)
            bs = utils.bytesToStr(bl.bcontent) + '.onion'
            if utils.validatePubKey(bl.signer) and utils.validateID(bs):
                daemon.active_services.append(b)
                daemon.active_services.append(bl.signer)
                daemon.services.create_server(bl.signer, bs)
    
    daemon.decrementThreadCount('service_creator')