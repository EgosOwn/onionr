from utils.identifyhome import identify_home
control_socket = f'{identify_home()}/torcontrol.sock'
tor_data_dir = f'{identify_home()}/tordata'