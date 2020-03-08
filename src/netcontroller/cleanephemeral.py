"""Onionr - Private P2P Communication.

Remove ephemeral services
"""
from filenuke.nuke import clean

from onionrutils.stringvalidators import validate_transport
from filepaths import ephemeral_services_file

from netcontroller.torcontrol.torcontroller import get_controller
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


def clean_ephemeral_services():
    """Remove transport's ephemeral services from respective controllers"""
    try:
        with open(ephemeral_services_file, 'r') as services:
            services = services.readlines()
            with get_controller() as torcontroller:
                for hs in services:
                    hs += '.onion'
                    if validate_transport(hs):
                        torcontroller.remove_ephemeral_hidden_service(hs)
    except FileNotFoundError:
        pass
    else:
        clean(ephemeral_services_file)
