from utils import identifyhome
import os
home = identifyhome.identify_home()
if not home.endswith('/'): home += '/'

app_root = os.path.dirname(os.path.realpath(__file__)) + '/../../'
usage_file = home + 'disk-usage.txt'
block_data_location = home + 'blocks/'
contacts_location = home + 'contacts/'
public_API_host_file = home + 'public-host.txt'
private_API_host_file = home + 'private-host.txt'
bootstrap_file_location = 'static-data/bootstrap-nodes.txt'
data_nonce_file = home + 'block-nonces.dat'
forward_keys_file = home + 'forward-keys.db'
cached_storage = home + 'cachedstorage.dat'
announce_cache = home + 'announcecache.dat'
export_location = home + 'block-export/'
upload_list = home + 'upload-list.json'
config_file = home + 'config.json'
daemon_mark_file = home + '/daemon-true.txt'
lock_file = home + 'onionr.lock'

site_cache = home + 'onionr-sites.txt'

tor_hs_loc = home + 'hs/'
tor_hs_address_file = home + 'hs/hostname'

data_nonce_file = home + 'block-nonces.dat'

keys_file = home + 'keys.txt'

onboarding_mark_file = home + 'onboarding-completed'

log_file = home + 'onionr.log'

ephemeral_services_file = home + 'ephemeral-services.list'

restarting_indicator = home + "is-restarting"
