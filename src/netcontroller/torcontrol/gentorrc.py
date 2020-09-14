"""Onionr - Private P2P Communication.

Generate a generate a torrc file for our Onionr instance
"""
import base64
import os
import subprocess
from typing import TYPE_CHECKING

from .. import getopenport
from . import customtorrc
from . import addbridges
from . import torbinary
from utils import identifyhome
import config

if TYPE_CHECKING:
    from netcontroller import NetController
    from onionrtypes import LoopBackIP
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

add_bridges = addbridges.add_bridges


def generate_torrc(net_controller: 'NetController',
                   api_server_ip: 'LoopBackIP'):
    """Generate a torrc file for our tor instance."""
    socks_port = net_controller.socksPort
    hs_port = net_controller.hsPort
    home_dir = identifyhome.identify_home()
    tor_config_location = home_dir + '/torrc'

    hs_ver = 'HiddenServiceVersion 3'

    """
    Set the Tor control password.
    Meant to make it harder to manipulate our Tor instance
    """
    plaintext = base64.b85encode(
        os.urandom(50)).decode()
    config.set('tor.controlpassword', plaintext, savefile=True)
    config.set('tor.socksport', socks_port, savefile=True)

    control_port = getopenport.get_open_port()

    config.set('tor.controlPort', control_port, savefile=True)

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
ControlPort """ + str(control_port) + """
HashedControlPassword """ + str(password) + """
    """
    if config.get('general.security_level', 1) == 0:
        torrc_data += """\nHiddenServiceDir """ + home_dir + """hs/
\n""" + hs_ver + """\n
HiddenServiceNumIntroductionPoints 20
HiddenServiceMaxStreams 500
HiddenServiceMaxStreamsCloseCircuit 1
HiddenServicePort 80 """ + api_server_ip + """:""" + str(hs_port)

    torrc_data = add_bridges(torrc_data)

    torrc_data += customtorrc.get_custom_torrc()

    torrc = open(tor_config_location, 'w')
    torrc.write(torrc_data)
    torrc.close()
