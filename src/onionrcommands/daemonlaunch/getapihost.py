"""Onionr - Private P2P Communication.

Wait for the api host to be available in the public api host file.
returns string of ip for the local public host interface
"""
from time import sleep

from filepaths import public_API_host_file
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


def get_api_host_until_available() -> str:
    """Wait for the api host to be available in the public api host file.

    returns string of ip for the local public host interface
    """
    api_host = ''
    while api_host == '':
        try:
            with open(public_API_host_file, 'r') as file:
                api_host = file.read()
        except FileNotFoundError:
            pass
        sleep(0.5)
    return api_host
