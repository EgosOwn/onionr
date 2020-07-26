"""Onionr - Private P2P Communication.

Dev utility to profile an Onionr subnetwork.
"""
import ujson as json

import config
from utils.bettersleep import better_sleep
from utils.gettransports import get as get_transports
from onionrutils import basicrequests
from onionrutils import epoch
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


def statistics_reporter(shared_state):
    server = config.get('statistics.server', '')
    if not config.get('statistics.i_dont_want_privacy', False) or \
            not server:
        return

    def compile_data():
        return {
            'time': epoch.get_epoch(),
            'adders': get_transports(),
            'peers': shared_state.get_by_string(
                'DeadSimpleKV').get('onlinePeers')
            }

    while True:
        better_sleep(5)
        data = compile_data()
        basicrequests.do_post_request(
            f'http://{server}/sendstats/' + get_transports()[0],
            data=json.dumps(data))
