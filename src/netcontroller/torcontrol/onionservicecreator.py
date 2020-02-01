"""Onionr - Private P2P Communication.

Create an ephemeral onion service
"""
from .torcontroller import get_controller
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


def create_onion_service(port=80):
    controller = get_controller()
    hs = controller.create_ephemeral_hidden_service(
        {80: port},
        key_type = 'NEW',
        key_content = 'ED25519-V3',
        await_publication=True,
        detached=True)
    return (hs.service_id, hs.private_key)
