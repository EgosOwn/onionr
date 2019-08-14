import netcontroller

def has_tor():
    return netcontroller.tor_binary() is not None