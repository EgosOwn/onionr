from utils import identifyhome
import filepaths
home = identifyhome.identify_home()
if not home.endswith('/'): home += '/'

address_info_db = '%saddress.db' % (home,)
user_id_info_db = '%susers.db' % (home,)
forward_keys_db = '%sforward-keys.db' % (home,)
blacklist_db = '%sblacklist.db' % (home,)