from stem.control import Controller

from .torfilepaths import control_socket


def get_socks():
    with Controller.from_socket_file(control_socket) as controller:
        return controller.get_listeners('SOCKS')
