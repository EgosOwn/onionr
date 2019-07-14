'''
    Onionr - Private P2P Communication

    god log function
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
import sys, time
from . import colors, raw, settings
colors = colors.Colors
def log(prefix, data, color = '', timestamp=True, fd = sys.stdout, prompt = True, terminal = False):
    '''
        Logs the data
        prefix : The prefix to the output
        data   : The actual data to output
        color  : The color to output before the data
    '''
    curTime = ''
    if timestamp:
        curTime = time.strftime("%m-%d %H:%M:%S") + ' '

    output = colors.reset + str(color) + ('[' + colors.bold + str(prefix) + colors.reset + str(color) + '] ' if prompt is True else '') + curTime + str(data) + colors.reset
    if not settings.get_settings() & settings.USE_ANSI:
        output = colors.filter(output)

    raw.raw(output, fd = fd, terminal = terminal)