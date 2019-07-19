'''
    Onionr - Private P2P Communication

    Check if the communicator is running
'''
'''
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
'''
import time, os
import filepaths
def is_communicator_running(timeout = 5, interval = 0.1):
    try:
        runcheck_file = filepaths.run_check_file

        if not os.path.isfile(runcheck_file):
            open(runcheck_file, 'w+').close()

        starttime = time.time()

        while True:
            time.sleep(interval)

            if not os.path.isfile(runcheck_file):
                return True
            elif time.time() - starttime >= timeout:
                return False
    except:
        return False