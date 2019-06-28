import sqlite3, os
from onionrutils import stringvalidators
def human_size(num, suffix='B'):
    '''
        Converts from bytes to a human readable format.
    '''
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

def size(path='.'):
    '''
        Returns the size of a folder's contents in bytes
    '''
    total = 0
    if os.path.exists(path):
        if os.path.isfile(path):
            total = os.path.getsize(path)
        else:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += size(entry.path)
    return total