from stem.control import Controller

import config

def get_controller():
    c = Controller.from_port(port=config.get('tor.controlPort'))
    c.authenticate(config.get('tor.controlpassword'))
    return c
