'''
    Onionr - Private P2P Communication

    confirm y/n cli prompt
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
import sys
from . import colors, settings
colors = colors.Colors
def confirm(default = 'y', message = 'Are you sure %s? '):
    '''
        Displays an "Are you sure" message, returns True for Y and False for N
        message: The confirmation message, use %s for (y/n)
        default: which to prefer-- y or n
    '''

    color = colors.fg.green + colors.bold

    default = default.lower()
    confirm = colors.bold
    if default.startswith('y'):
        confirm += '(Y/n)'
    else:
        confirm += '(y/N)'
    confirm += colors.reset + color

    output = colors.reset + str(color) + '... ' + colors.reset + str(message) + colors.reset

    if not get_settings() & settings.USE_ANSI:
        output = colors.filter(output)

    sys.stdout.write(output.replace('%s', confirm))

    inp = input().lower()

    if 'y' in inp:
        return True
    if 'n' in inp:
        return False
    else:
        return default == 'y'