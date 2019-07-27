import netcontroller

def has_tor():
    if netcontroller.tor_binary() is None:
        return False
    return True