'''
    Onionr - Private P2P Communication

    get a line of input from stdin
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
def readline(message = ''):
    '''
        Takes in input from the console, not stored in logs
        message: The message to display before taking input
    '''

    color = colors.fg.green + colors.bold
    output = colors.reset + str(color) + '... ' + colors.reset + str(message) + colors.reset

    if not settings.get_settings() & settings.USE_ANSI:
        output = colors.filter(output)

    sys.stdout.write(output)

    return input()