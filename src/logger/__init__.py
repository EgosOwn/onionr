"""
Onionr - Private P2P Communication

We use built in logging but with a custom formatter for colors and such
"""
import logging

from filepaths import log_file
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

# credit: https://stackoverflow.com/a/384076
# license: https://creativecommons.org/licenses/by-sa/4.0/
class ConsoleFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    green = "\x1b[38;5;82m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_default = "%(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format_info = "%(message)s - (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format_default + reset,
        logging.INFO: green + format_info + reset,
        logging.WARNING: yellow + format_default + reset,
        logging.ERROR: red + format_default + reset,
        logging.CRITICAL: bold_red + format_default + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class FileFormatter(logging.Formatter):


    format_default = "%(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format_info = "%(message)s - (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: format_default,
        logging.INFO: format_info,
        logging.WARNING: format_default,
        logging.ERROR: format_default,
        logging.CRITICAL: format_default
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


#logging.basicConfig(level=logging.ERROR, format='%(message)s ')
log = logging.getLogger('onionr')
log.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

ch.setFormatter(ConsoleFormatter())


def enable_file_logging():
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(FileFormatter())
    log.addHandler(fh)

def disable_console_logging():
    log.removeHandler(ch)

def enable_console_logging():
    log.addHandler(ch)
enable_console_logging()
