"""Onionr - Private P2P Communication.

Test Onionr as it is running
"""
import os
from secrets import SystemRandom

import logger
from onionrutils import epoch

from . import uicheck, inserttest, stresstest
from . import ownnode
from .webpasstest import webpass_test
from .osver import test_os_ver_endpoint
from .clearnettor import test_clearnet_tor_request
from .housekeeping import test_inserted_housekeeping
from .lanservertest import test_lan_server
from .sneakernettest import test_sneakernet_import
from .dnsrebindingtest import test_dns_rebinding
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
             test_clearnet_tor_request,
             test_inserted_housekeeping,
             test_lan_server,
             sneakernettest.test_sneakernet_import,
             test_dns_rebinding
             ]

SUCCESS_FILE = os.path.dirname(os.path.realpath(__file__)) + '/../../tests/runtime-result.txt'


class OnionrRunTestManager:
    def __init__(self):
        self.success: bool = True
        self.run_date: int = 0

    def run_tests(self):
        tests = list(RUN_TESTS)
        SystemRandom().shuffle(tests)
        cur_time = epoch.get_epoch()
        logger.info(f"Doing runtime tests at {cur_time}")

        try:
            os.remove(SUCCESS_FILE)
        except FileNotFoundError:
            pass

        done_count: int = 0
        total_to_do: int = len(tests)

        try:
            for i in tests:
                last = i
                logger.info("[RUNTIME TEST] " + last.__name__ + " started",
                            terminal=True, timestamp=True)
                i(self)
                done_count += 1
                logger.info("[RUNTIME TEST] " + last.__name__ +
                            f" passed {done_count}/{total_to_do}",
                            terminal=True, timestamp=True)
        except (ValueError, AttributeError):
            logger.error(last.__name__ + ' failed assertions', terminal=True)
        except Exception as e:
            logger.error(last.__name__ + ' failed with non-asserting exception')
            logger.error(str(e))
        else:
            ep = str(epoch.get_epoch())
            logger.info(f'All runtime tests passed at {ep}', terminal=True)
            with open(SUCCESS_FILE, 'w') as f:
                f.write(ep)

