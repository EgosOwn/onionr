from typing import Union, Tuple
import tarfile
import io
import os

import unpaddedbase32

from coredb import blockmetadb
from onionrblocks import onionrblockapi
from onionrblocks import insert

# Import types. Just for type hiting
from onionrtypes import UserID, DeterministicKeyPassphrase, BlockHash

from onionrcrypto import generate_deterministic

def find_site_gzip(user_id: str)->tarfile.TarFile:
    """Return verified site tar object"""
    sites = blockmetadb.get_blocks_by_type('osite')
    user_site = None
    user_id = unpaddedbase32.repad(user_id)
    for site in sites:
        block = onionrblockapi.Block(site)
        if block.isSigner(user_id):
            user_site = block
    if not user_site is None:
        return tarfile.open(fileobj=io.BytesIO(user_site.bcontent), mode='r')
    return None

def get_file(user_id, file)->Union[bytes, None]:
    """Get a site file content"""
    ret_data = ""
    site = find_site_gzip(user_id)
    if site is None: return None
    for t_file in site.getmembers():
        if t_file.name.replace('./', '') == file:
            return site.extractfile(t_file)
    return None

def create_site(admin_pass: DeterministicKeyPassphrase, directory:str='.')->Tuple[UserID, BlockHash]:
    public_key, private_key = generate_deterministic(admin_pass)

    raw_tar = io.BytesIO()

    tar = tarfile.open(mode='x:gz', fileobj=raw_tar)
    tar.add(directory)
    tar.close()

    raw_tar.seek(0)

    block_hash = insert(raw_tar.read(), header='osite', signing_key=private_key, sign=True)

    return (public_key, block_hash)
