import netcontroller
import config

def restart(comm_inst):
    if not config.get('tor.use_existing_tor', False):
        net = comm_inst.shared_state.get(netcontroller.NetController)
        net.killTor()
        net.startTor()
