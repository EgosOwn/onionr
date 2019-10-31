from typing import Union
import tarfile
import io

from coredb import blockmetadb
from onionrblocks import onionrblockapi

def find_site_gzip(user_id: str)->str:
    sites = blockmetadb.get_blocks_by_type('osite')
    for site in sites:
        if onionrblockapi.Block(site).isSigner(user_id):
            return tarfile.open(fileobj=io.BytesIO(site.bcontent), mode='r')
    return None

def get_file(user_id, file)->Union[bytes, None]:
    ret_data = ""
    site = find_site_gzip(user_id)
    if site is None: return None
    for file in site.getmembers():
        if file.name == file:
            return site.extractfile(file)
    return None
