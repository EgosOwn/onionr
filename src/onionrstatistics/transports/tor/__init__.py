"""Onionr - Private P2P Communication.

tor stats info
"""
import ujson as json
from stem import CircStatus

import logger
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


class TorStats:
    def __init__(self):
        self.circuits = {}
        self.json_data = ""
        self.controller = None

    def get_json(self):
        """Refresh circuits then serialize them into form:

        "nodes": list of tuples containing fingerprint and nickname strings"
        "purpose": https://stem.torproject.org/api/control.html#stem.CircPurpose
        """
        if self.controller is None:
            self.controller = get_controller()
        if not self.controller.is_alive():
            logger.info(f'{__name__} reconnecting to tor control')
            self.controller = get_controller()
        self.get_circuits()
        json_serialized = {}
        for circuit in self.circuits.keys():
            json_serialized[circuit] = {
                "nodes": [],
                "purpose": self.circuits[circuit][1]
            }
            for entry in self.circuits[circuit][0]:
                json_serialized[circuit]["nodes"].append({'finger': entry[0],
                                                         'nick': entry[1]})
        self.json_data = json.dumps(json_serialized)
        return self.json_data

    def get_circuits(self):
        """Update the circuit dictionary"""
        circuits = {}
        for circ in list(sorted(self.controller.get_circuits())):
            if circ.status != CircStatus.BUILT:
                continue
            circuits[circ.id] = (circ.path, circ.purpose)
        self.circuits = circuits

