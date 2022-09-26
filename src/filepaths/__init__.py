from utils import identifyhome
import os
home = identifyhome.identify_home()
if not home.endswith('/'): home += '/'

app_root = os.path.dirname(os.path.realpath(__file__)) + '/../../'

gossip_server_socket_file = home + 'gossip-server.sock'

config_file = home + 'config.json'
lock_file = home + 'onionr.lock'
pid_file = home + 'onionr.pid'

log_file = home + 'onionr.log'
