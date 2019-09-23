'''
    $name plugin template file.
    Generated on $date by $user.
'''

plugin_name = '$name'

def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    pluginapi = api

