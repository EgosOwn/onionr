from . import announce, upload, getblocks, endpoints

announce = announce.handle_announce # endpoint handler for accepting peer announcements
upload = upload.accept_upload # endpoint handler for accepting public uploads
public_block_list = getblocks.get_public_block_list # endpoint handler for getting block lists
public_get_block_data = getblocks.get_block_data # endpoint handler for responding to peers requests for block data