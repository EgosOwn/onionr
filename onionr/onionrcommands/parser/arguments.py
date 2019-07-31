from .. import onionrstatistics, version, daemonlaunch
import onionrexceptions
def get_arguments():
    '''This is a function because we need to be able to dynamically modify them with plugins'''
    args = {
        ('details', 'info'): onionrstatistics.show_details,
        ('version'): version.version,
        ('start', 'daemon'): daemonlaunch.start
    }
    return args

def get_help():
    return

def get_func(argument):
    argument = argument.lower()
    args = get_arguments()

    for arg in args.keys(): # Iterate command alias sets
        if argument in arg: # If our argument is in the current alias set, return the command function
            return args[arg]
    raise onionrexceptions.NotFound