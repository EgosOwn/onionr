'''
    $name plugin template file.
    Generated on $date by $user.
'''

# Imports some useful libraries
import logger, config

plugin_name = '$name'

def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    # Doing this makes it so that the other functions can access the api object
    # by simply referencing the variable `pluginapi`.
    global pluginapi
    pluginapi = api

    return

def on_start(api, data = None):
    '''
        This event can be called for multiple reasons:
        1) The daemon is starting
        2) The user called `onionr --start-plugins` or `onionr --reload-plugins`
        3) For whatever reason, the plugins are reloading
    '''

    return

def on_stop(api, data = None):
    '''
        This event can be called for multiple reasons:
        1) The daemon is stopping
        2) The user called `onionr --stop-plugins` or `onionr --reload-plugins`
        3) For whatever reason, the plugins are reloading
    '''

    return
