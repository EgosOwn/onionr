from utils.identifyhome import identify_home
control_socket = f'{identify_home()}/torcontrol.sock'
tor_data_dir = f'{identify_home()}/tordata'
peer_database_file = f'{identify_home()}/tor-peers'
