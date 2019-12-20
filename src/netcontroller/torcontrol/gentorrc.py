import base64
import os
import subprocess

from .. import getopenport
from . import customtorrc
from . import addbridges
from . import torbinary
from utils import identifyhome
import config

add_bridges = addbridges.add_bridges


def generate_torrc(net_controller, api_server_ip):
    """
        Generate a torrc file for our tor instance
    """
    socks_port = net_controller.socksPort
    hs_ver = '# v2 onions'
    hs_port = net_controller.hsPort
    home_dir = identifyhome.identify_home()
    tor_config_location = home_dir + '/torrc'

    if config.get('tor.v3onions'):
        hs_ver = 'HiddenServiceVersion 3'

    """
    Set the Tor control password.
    Meant to make it harder to manipulate our Tor instance
    """
    plaintext = base64.b64encode(os.urandom(50)).decode()
    config.set('tor.controlpassword', plaintext, savefile=True)
    config.set('tor.socksport', socks_port, savefile=True)

    controlPort = getopenport.get_open_port()

    config.set('tor.controlPort', controlPort, savefile=True)

    hashedPassword = subprocess.Popen([torbinary.tor_binary(),
                                      '--hash-password',
                                       plaintext],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    for line in iter(hashedPassword.stdout.readline, b''):
        password = line.decode()
        if 'warn' not in password:
            break

    torrc_data = """SocksPort """ + str(socks_port) + """ OnionTrafficOnly
DataDirectory """ + home_dir + """tordata/
CookieAuthentication 1
KeepalivePeriod 40
CircuitsAvailableTimeout 86400
ControlPort """ + str(controlPort) + """
HashedControlPassword """ + str(password) + """
    """
    if config.get('general.security_level', 1) == 0:
        torrc_data += """\nHiddenServiceDir """ + home_dir + """hs/
\n""" + hs_ver + """\n
HiddenServiceNumIntroductionPoints 6
HiddenServiceMaxStreams 100
HiddenServiceMaxStreamsCloseCircuit 1
HiddenServicePort 80 """ + api_server_ip + """:""" + str(hs_port)

    torrc_data = add_bridges(torrc_data)

    torrc_data += customtorrc.get_custom_torrc()

    torrc = open(tor_config_location, 'w')
    torrc.write(torrc_data)
    torrc.close()
