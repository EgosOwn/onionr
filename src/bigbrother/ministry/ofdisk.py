"""Onionr - Private P2P Communication.

Log (not block) read/write of non-user data files and non-python lib files
"""
from utils.identifyhome import identify_home
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


def detect_disk_access(info):
    if type(info[0]) is int: return

    if '/dev/null' == info[0]: return

    whitelist = [identify_home(), 'onionr/src/', '/site-packages/', '/usr/lib64/']

    for item in whitelist:
        if item in info[0]:
            return

    if identify_home() not in info[0]:
        if 'proc' not in info[0]:  # if it is, it is onionr stats
            logger.warn(f'[DISK MINISTRY] {info}')
