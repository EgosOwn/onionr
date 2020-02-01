from stem.control import Controller

import config
config.reload()


def get_controller() -> Controller:
    """Create and return a Tor controller connection."""
    port = config.get('tor.controlPort', 0)
    password = config.get('tor.controlpassword', '')
    if config.get('tor.use_existing_tor', False):
        port = config.get('tor.existing_control_port', 0)
        password = config.get('tor.existing_control_password', '')
    c = Controller.from_port(port=port)
    c.authenticate(password)
    return c
