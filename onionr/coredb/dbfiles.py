from utils import identifyhome
home = identifyhome.identify_home()
if not home.endswith('/'): home += '/'

block_meta_db = '%sblock-metadata.db'