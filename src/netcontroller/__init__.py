from . import getopenport
import os
from shutil import which


def tor_binary():
    """Return tor binary path or none if not exists"""
    tor_path = './tor'
    if not os.path.exists(tor_path):
        tor_path = which('tor')
    return tor_path
