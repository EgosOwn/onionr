'''
    Onionr - Private P2P Communication

    logger settings
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
import os
from utils import identifyhome
import filepaths

data_home = os.environ.get('ONIONR_LOG_DIR', identifyhome.identify_home())
# Use the bitwise operators to merge these settings
USE_ANSI = 0b100
if os.name == 'nt':
    USE_ANSI = 0b000
OUTPUT_TO_CONSOLE = 0b010
OUTPUT_TO_FILE = 0b001

LEVEL_DEBUG = 1
LEVEL_INFO = 2
LEVEL_WARN = 3
LEVEL_ERROR = 4
LEVEL_FATAL = 5
LEVEL_IMPORTANT = 6

MAX_LOG_FILE_LINES = 10000

_type = OUTPUT_TO_CONSOLE | USE_ANSI # the default settings for logging
_level = LEVEL_DEBUG # the lowest level to log
# the file to log to
_outputfile = filepaths.log_file

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

def get_level()->int:
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