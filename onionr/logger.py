'''
    Onionr - P2P Microblogging Platform & Social network

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

import re, sys, time, traceback, os

class colors:
    '''
        This class allows you to set the color if ANSI codes are supported
    '''
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    italics='\033[3m'

    class fg:
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'
    class bg:
        black='\033[40m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        lightgrey='\033[47m'
    @staticmethod
    def filter(data):
        return re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]').sub('', str(data))

'''
    Use the bitwise operators to merge these settings
'''
USE_ANSI = 0b000 if os.name == 'nt' else 0b100
OUTPUT_TO_CONSOLE = 0b010
OUTPUT_TO_FILE = 0b001

LEVEL_DEBUG = 1
LEVEL_INFO = 2
LEVEL_WARN = 3
LEVEL_ERROR = 4
LEVEL_FATAL = 5
LEVEL_IMPORTANT = 6

_type = OUTPUT_TO_CONSOLE | USE_ANSI # the default settings for logging
_level = LEVEL_DEBUG # the lowest level to log
_outputfile = 'data/onionr.log' # the file to log to

def set_settings(type):
    '''
        Set the settings for the logger using bitwise operators
    '''

    global _type
    _type = type

def get_settings():
    '''
        Get settings from the logger
    '''

    return _type

def set_level(level):
    '''
        Set the lowest log level to output
    '''

    global _level
    _level = level

def get_level():
    '''
        Get the lowest log level currently being outputted
    '''

    return _level

def set_file(outputfile):
    '''
        Set the file to output to, if enabled
    '''

    global _outputfile
    _outputfile = outputfile

def get_file():
    '''
        Get the file to output to
    '''

    return _outputfile

def raw(data, fd = sys.stdout, terminal = False):
    '''
        Outputs raw data to console without formatting
    '''

    if terminal and (get_settings() & OUTPUT_TO_CONSOLE):
        try:
            ts = fd.write('%s\n' % data)
        except OSError:
            pass
    if get_settings() & OUTPUT_TO_FILE:
        try:
            with open(_outputfile, "a+") as f:
                f.write(colors.filter(data) + '\n')
        except OSError:
            pass

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
    if not get_settings() & USE_ANSI:
        output = colors.filter(output)

    raw(output, fd = fd, terminal = terminal)

def readline(message = ''):
    '''
        Takes in input from the console, not stored in logs
        message: The message to display before taking input
    '''

    color = colors.fg.green + colors.bold
    output = colors.reset + str(color) + '... ' + colors.reset + str(message) + colors.reset

    if not get_settings() & USE_ANSI:
        output = colors.filter(output)

    sys.stdout.write(output)

    return input()

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

    if not get_settings() & USE_ANSI:
        output = colors.filter(output)

    sys.stdout.write(output.replace('%s', confirm))

    inp = input().lower()

    if 'y' in inp:
        return True
    if 'n' in inp:
        return False
    else:
        return default == 'y'

# debug: when there is info that could be useful for debugging purposes only
def debug(data, error = None, timestamp = True, prompt = True, terminal = True, level = LEVEL_DEBUG):
    if get_level() <= level:
        log('/', data, timestamp = timestamp, prompt = prompt, terminal = terminal)
    if not error is None:
        debug('Error: ' + str(error) + parse_error())

# info: when there is something to notify the user of, such as the success of a process
def info(data, timestamp = False, prompt = True, terminal = True, level = LEVEL_INFO):
    if get_level() <= level:
        log('+', data, colors.fg.green, timestamp = timestamp, prompt = prompt, terminal = terminal)

# warn: when there is a potential for something bad to happen
def warn(data, error = None, timestamp = True, prompt = True, terminal = True, level = LEVEL_WARN):
    if not error is None:
        debug('Error: ' + str(error) + parse_error())
    if get_level() <= level:
        log('!', data, colors.fg.orange, timestamp = timestamp, prompt = prompt, terminal = terminal)

# error: when only one function, module, or process of the program encountered a problem and must stop
def error(data, error = None, timestamp = True, prompt = True, terminal = True, level = LEVEL_ERROR):
    if get_level() <= level:
        log('-', data, colors.fg.red, timestamp = timestamp, fd = sys.stderr, prompt = prompt, terminal = terminal)
    if not error is None:
        debug('Error: ' + str(error) + parse_error())

# fatal: when the something so bad has happened that the program must stop
def fatal(data, error = None, timestamp = True, prompt = True, terminal = True, level = LEVEL_FATAL):
    if not error is None:
        debug('Error: ' + str(error) + parse_error(), terminal = terminal)
    if get_level() <= level:
        log('#', data, colors.bg.red + colors.fg.green + colors.bold, timestamp = timestamp, fd = sys.stderr, prompt = prompt, terminal = terminal)

# returns a formatted error message
def parse_error():
    details = traceback.extract_tb(sys.exc_info()[2])
    output = ''

    for line in details:
        output += ('\n    ... ' + colors.bold + '%s' + colors.reset + ' in %s:' + colors.bold + '%i' + colors.reset) % (line[2], line[0], line[1])

    if not (get_settings() & USE_ANSI):
        output = colors.filter(output)

    return output
