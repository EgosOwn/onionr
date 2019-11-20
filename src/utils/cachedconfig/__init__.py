from onionrutils import localcommand
import config
config.reload()
running_detected = False # if we know the api server is running
first_get = True

def config_get(key):
    ret_data = False
    if running_detected or first_get:
        first_get = False
        ret_data = localcommand.local_command('/config/get/' + key)
    if ret_data == False:
        running_detected = False
        ret_data = config.get(key)
    else:
        running_detected = False
    return ret_data