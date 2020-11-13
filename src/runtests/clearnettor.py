"""Onionr - Private P2P Communication.

Ensure that clearnet cannot be reached
"""
from onionrutils.basicrequests import do_get_request
from onionrutils import localcommand
import logger
import config
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


def test_clearnet_tor_request(testmanager):
    """Ensure that Tor cannot request clearnet address.

    Does not run if Tor is being reused
    """

    config.reload()
    leak_result = ""

    if config.get('tor.use_existing_tor', False):
        logger.warn(
            "Can't ensure Tor reqs to clearnet won't happen when reusing Tor")
        return


    socks_port = localcommand.local_command('/gettorsocks')

    # Don't worry, this request isn't meant to go through,
    # but if it did it would be through Tor

    try:
        leak_result: str = do_get_request(
            'https://example.com/notvalidpage',
            port=socks_port, ignoreAPI=True).lower()
    except AttributeError:
        leak_result = ""
    except Exception as e:
        logger.warn(str(e))
    try:
        if 'example' in leak_result:
            logger.error('Tor was able to request a clearnet site')
            raise ValueError('Tor was able to request a clearnet site')
    except TypeError:
        pass
