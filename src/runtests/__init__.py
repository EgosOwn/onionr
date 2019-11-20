"""
    Onionr - Private P2P Communication

    Test Onionr as it is running
"""
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
import logger
from onionrutils import epoch

from . import uicheck, inserttest, stresstest

RUN_TESTS = [uicheck.check_ui, inserttest.insert_bin_test, stresstest.stress_test_block_insert]

class OnionrRunTestManager:
    def __init__(self):
        self.success:bool = True
        self.run_date:int = 0
    
    def run_tests(self):
        cur_time = epoch.get_epoch()
        logger.info(f"Doing runtime tests at {cur_time}")
        try:
            for i in RUN_TESTS:
                last = i
                i(self)
                logger.info(last.__name__ + " passed")
        except ValueError:
            logger.error(last.__name__ + ' failed')
    