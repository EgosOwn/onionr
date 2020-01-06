from utils import identifyhome
import filepaths
home = identifyhome.identify_home()
if not home.endswith('/'): home += '/'

block_meta_db = '%sblock-metadata.db' % (home)
block_data_db = '%s/block-data.db' % (filepaths.block_data_location,)
address_info_db = '%saddress.db' % (home,)
user_id_info_db = '%susers.db' % (home,)
forward_keys_db = '%sforward-keys.db' % (home,)
blacklist_db = '%sblacklist.db' % (home,)