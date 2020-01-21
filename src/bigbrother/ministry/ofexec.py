"""Onionr - Private P2P Communication.

Prevent eval/exec/os.system and log it
"""
import base64
import platform

import logger
from utils import identifyhome
from onionrexceptions import ArbitraryCodeExec
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


def block_system(cmd):
    """Prevent os.system except for whitelisted commands+contexts."""
    allowed = 'taskkill /PID '
    is_ok = False
    if platform.system() == 'Windows':
        if cmd.startswith(allowed):
            for c in cmd.split(allowed)[1]:
                if not c.isalnum() or c not in ('/', 'F', ' '):
                    break
            else:
                is_ok = True
    if not is_ok:
        logger.warn('POSSIBLE EXPLOIT DETECTED, SEE LOGS', terminal=True)
        logger.warn(f'POSSIBLE EXPLOIT: shell command not in whitelist: {cmd}')
        raise ArbitraryCodeExec('os.system command not in whitelist')


def block_exec(event, info):
    """Prevent arbitrary code execution in eval/exec and log it."""
    # because libraries have stupid amounts of compile/exec/eval,
    # We have to use a whitelist where it can be tolerated
    whitelisted_code = [
                        'netrc.py',
                        'shlex.py',
                        '<werkzeug routing>',
                        'werkzeug/test.py',
                        'multiprocessing/popen_fork.py',
                        'multiprocessing/util.py',
                        'multiprocessing/connection.py',
                        'onionrutils/escapeansi.py',
                        'stem/connection.py',
                        'stem/response/add_onion.py',
                        'stem/response/authchallenge.py',
                        'stem/response/getinfo.py',
                        'stem/response/getconf.py',
                        'stem/response/mapaddress.py',
                        'stem/response/protocolinfo.py'
                       ]
    home = identifyhome.identify_home()

    code_b64 = base64.b64encode(info[0].co_code).decode()

    for source in whitelisted_code:
        if info[0].co_filename.endswith(source):
            return

    if home + 'plugins/' in info[0].co_filename:
        return

    logger.warn('POSSIBLE EXPLOIT DETECTED, SEE LOGS', terminal=True)
    logger.warn('POSSIBLE EXPLOIT DETECTED: ' + info[0].co_filename)
    logger.warn('Prevented exec/eval. Report this with the sample below')
    logger.warn(f'{event} code in base64 format: {code_b64}')
    raise ArbitraryCodeExec("Arbitrary code (eval/exec) detected.")
