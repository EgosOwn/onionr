from utils.identifyhome import identify_home
SERVER_SOCKET = identify_home() + "torgossip.sock"
HOSTNAME_FILE = identify_home() + "torgossip-hostname"
GOSSIP_PORT = 2020