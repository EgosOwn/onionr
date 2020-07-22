import re


def escape_ANSI(line):
    '''
        Remove ANSI escape codes from a string with regex

        adapted from: https://stackoverflow.com/a/38662876 by user https://stackoverflow.com/users/802365/%c3%89douard-lopez
        cc-by-sa-3 license https://creativecommons.org/licenses/by-sa/3.0/
    '''
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)
