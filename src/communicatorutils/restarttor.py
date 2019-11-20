import netcontroller
def restart(comm_inst):
    net = comm_inst.shared_state.get(netcontroller.NetController)
    net.killTor()
    net.startTor()
