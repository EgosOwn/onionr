from utils import identifyhome
home = identifyhome.identify_home()
if not home.endswith('/'): home += '/'

block_meta_db = '%sblock-metadata.db' % (home,)
block_data_db = '%sblocks/block-data.db' % (home,)
daemon_queue_db = '%sdaemon-queue.db' % (home,)
address_info_db = '%saddress.db' % (home,)
user_id_info_db = '%susers.db' % (home,)
forward_keys_db = '%sforward-keys.db' % (home,)