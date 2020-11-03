from . import torcontroller


def enable_tor_network_connection():
    with torcontroller.get_controller() as controller:
        c.set_conf("DisableNetwork", 0)


def disable_tor_network_connection():
    with torcontroller.get_controller() as controller:
        c.set_conf("DisableNetwork", 1)
