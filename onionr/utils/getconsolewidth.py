import os
def get_console_width():
    '''
        Returns an integer, the width of the terminal/cmd window
    '''

    columns = 80

    try:
        columns = int(os.popen('stty size', 'r').read().split()[1])
    except:
        # if it errors, it's probably windows, so default to 80.
        pass

    return columns