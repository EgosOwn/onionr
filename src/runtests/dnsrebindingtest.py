"""Onionr - Private P2P Communication.

Test apis for dns rebinding
"""
import config
import requests
from filepaths import private_API_host_file, public_API_host_file
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


def test_dns_rebinding(test_manager):
    f = ''
    with open(private_API_host_file, 'r') as f:
        host = f.read()
    private_api_port = config.get('client.client.port')

    if requests.get(f'http://{host}:{private_api_port}/ping', headers={'host': 'example.com'}) == 'pong!':
        raise ValueError('DNS rebinding failed')
    logger.info('It is normal to see 403 errors right now', terminal=True)

    if config.get('general.security_level', 0) > 0 or not config.get('transports.tor', True):
        return
    public_api_port = config.get('client.public.port')
    f = ''
    with open(public_API_host_file, 'r') as f:
        host = f.read()

    if requests.get(f'http://{host}:{public_api_port}/ping', headers={'host': 'example.com'}) == 'pong!':
        raise ValueError('DNS rebinding failed')
    logger.info('It is normal to see 403 errors right now', terminal=True)


