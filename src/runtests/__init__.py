"""Onionr - Private P2P Communication.

Test Onionr as it is running
"""
import os

import logger
from onionrutils import epoch

from . import uicheck, inserttest, stresstest
from . import ownnode
from .webpasstest import webpass_test
from .osver import test_os_ver_endpoint
from .clearnettor import test_clearnet_tor_request
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

RUN_TESTS = [uicheck.check_ui,
             inserttest.insert_bin_test,
             ownnode.test_tor_adder,
             ownnode.test_own_node,
             stresstest.stress_test_block_insert,
             webpass_test,
             test_os_ver_endpoint,
             test_clearnet_tor_request
             ]

SUCCESS_FILE = os.path.dirname(os.path.realpath(__file__)) + '/../../tests/runtime-result.txt'


class OnionrRunTestManager:
    def __init__(self):
        self.success: bool = True
        self.run_date: int = 0

    def run_tests(self):
        cur_time = epoch.get_epoch()
        logger.info(f"Doing runtime tests at {cur_time}")

        try:
            os.remove(SUCCESS_FILE)
        except FileNotFoundError:
            pass

        try:
            for i in RUN_TESTS:
                last = i
                i(self)
                logger.info("[RUNTIME TEST] " + last.__name__ + " passed")
        except (ValueError, AttributeError):
            logger.error(last.__name__ + ' failed')
        else:
            ep = str(epoch.get_epoch())
            logger.info(f'All runtime tests passed at {ep}')
            with open(SUCCESS_FILE, 'w') as f:
                f.write(ep)

