"""Onionr - Private P2P Communication.

Create an ephemeral onion service
"""
import stem

from .torcontroller import get_controller

from filepaths import ephemeral_services_file

import logger
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


def create_onion_service(port=80, record_to_service_removal_file=True):
    try:
        controller = get_controller()
    except stem.SocketError:
        logger.error("Could not connect to Tor control")
        raise
    hs = controller.create_ephemeral_hidden_service(
        {80: port},
        key_type='NEW',
        key_content='ED25519-V3',
        await_publication=True,
        detached=True)
    if record_to_service_removal_file:
        with open(ephemeral_services_file, 'a') as service_file:
            service_file.write(hs.service_id + '\n')
    return (hs.service_id, hs.private_key)
