"""Onionr - Private P2P Communication.

LAN manager
"""
from typing import TYPE_CHECKING
from threading import Thread
if TYPE_CHECKING:
    from toomanyobjs import TooMany

from .discover import learn_services, advertise_service
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


class LANManager:
    """Initialize and start/top LAN transport threads."""

    def __init__(self, too_many: "TooMany"):
        self.too_many = too_many
        self.peers: "exploded IP Address string" = []

    def start(self):
        Thread(target=learn_services, daemon=True).start()
        Thread(target=advertise_service, daemon=True).start()

