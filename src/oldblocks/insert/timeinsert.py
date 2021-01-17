"""Onionr - Private P2P Communication.

Wrapper to insert blocks with variable delay
"""
from . import main
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


def time_insert(*args, **kwargs):
    """Block insert wrapper to allow for insertions independent of mixmate.

    Takes exact args as insert_block, with additional keyword:
    delay=n; where n=seconds to tell initial nodes to delay share for.

    defaults to 0 or previously set value in current block meta
    """
    try:
        kwargs['meta']
    except KeyError:
        kwargs['meta'] = {}

    try:
        delay = int(kwargs['meta']['dly'])
    except KeyError:
        delay = 0
    try:
        delay = kwargs['delay']
        del kwargs['delay']
    except KeyError:
        delay = 0

    # Ensure delay >=0
    if delay < 0:
        raise ValueError('delay cannot be less than 0')

    kwargs['meta']['dly'] = delay

    return main.insert_block(*args, **kwargs)
