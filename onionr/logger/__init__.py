'''
    Onionr - Private P2P Communication

    This file handles all operations involving logging
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

import sys, traceback

from . import colors, readline, log, raw, confirm, colors, settings
colors = colors.Colors
readline = readline.readline
log = log.log
raw = raw.raw
confirm = confirm.confirm

# debug: when there is info that could be useful for debugging purposes only
def debug(data: str, error = None, timestamp = True, prompt = True, terminal = False, level = settings.LEVEL_DEBUG):
    if settings.get_level() <= level:
        log('/', data, timestamp = timestamp, prompt = prompt, terminal = terminal)
    if not error is None:
        debug('Error: ' + str(error) + parse_error())

# info: when there is something to notify the user of, such as the success of a process
def info(data: str, timestamp = False, prompt = True, terminal = False, level = settings.LEVEL_INFO):
    if settings.get_level() <= level:
        log('+', data, colors.fg.green, timestamp = timestamp, prompt = prompt, terminal = terminal)

# warn: when there is a potential for something bad to happen
def warn(data: str, error = None, timestamp = True, prompt = True, terminal = False, level = settings.LEVEL_WARN):
    if not error is None:
        debug('Error: ' + str(error) + parse_error())
    if settings.get_level() <= level:
        log('!', data, colors.fg.orange, timestamp = timestamp, prompt = prompt, terminal = terminal)

# error: when only one function, module, or process of the program encountered a problem and must stop
def error(data: str, error = None, timestamp = True, prompt = True, terminal = False, level = settings.LEVEL_ERROR):
    if settings.get_level() <= level:
        log('-', data, colors.fg.red, timestamp = timestamp, fd = sys.stderr, prompt = prompt, terminal = terminal)
    if not error is None:
        debug('Error: ' + str(error) + parse_error())

# fatal: when the something so bad has happened that the program must stop
def fatal(data: str, error = None, timestamp=True, prompt = True, terminal = False, level = settings.LEVEL_FATAL):
    if not error is None:
        debug('Error: ' + str(error) + parse_error(), terminal = terminal)
    if settings.get_level() <= level:
        log('#', data, colors.bg.red + colors.fg.green + colors.bold, timestamp = timestamp, fd = sys.stderr, prompt = prompt, terminal = terminal)

# returns a formatted error message
def parse_error():
    details = traceback.extract_tb(sys.exc_info()[2])
    output = ''

    for line in details:
        output += '\n    ... module %s in  %s:%i' % (line[2], line[0], line[1])

    return output
