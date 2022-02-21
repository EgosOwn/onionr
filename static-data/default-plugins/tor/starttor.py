from time import sleep

import stem.process

from utils.identifyhome import identify_home

from torfilepaths import control_socket
from torfilepaths import tor_data_dir


def start_tor():
    tor_process = stem.process.launch_tor_with_config(
        config={
            'SocksPort': 'auto OnionTrafficOnly',
            'DataDirectory': tor_data_dir,
            'ControlSocket': control_socket,
        },
        completion_percent=100
    )
