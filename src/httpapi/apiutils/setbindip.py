import gevent
from gevent import socket, sleep
import secrets, random
import config, logger
import os

# Hacky monkey patch so we can bind random localhosts without gevent trying to switch with an empty hub
socket.getfqdn = lambda n: n

def _get_acceptable_random_number()->int:
    """Return a cryptographically random number in the inclusive range (1, 255)"""
    number = 0
    while number == 0:
        number = secrets.randbelow(0xFF)
    return number

def set_bind_IP(filePath=''):
    '''Set a random localhost IP to a specified file (intended for private or public API localhost IPs)'''
    if config.get('general.random_bind_ip', True):
        hostOctets = []
        # Build the random localhost address
        for i in range(3):
            hostOctets.append(str(_get_acceptable_random_number()))
        hostOctets = ['127'] + hostOctets
        # Convert the localhost address to a normal string address
        data = '.'.join(hostOctets)
        
        # Try to bind IP. Some platforms like Mac block non normal 127.x.x.x
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((data, 0))
        except OSError:
            # if mac/non-bindable, show warning and default to 127.0.0.1
            logger.warn('Your platform appears to not support random local host addresses 127.x.x.x. Falling back to 127.0.0.1.')
            data = '127.0.0.1'
        s.close()
    else:
        data = '127.0.0.1'
    if filePath != '':
        with open(filePath, 'w') as bindFile:
            bindFile.write(data)
    return data