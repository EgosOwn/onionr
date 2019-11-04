from typing import Union
import tarfile
import io
import os

from coredb import blockmetadb
from onionrblocks import onionrblockapi
from onionrblocks import insert
from onionrtypes import UserID, DeterministicKeyPassphrase # Import types. Just for type hiting
from onionrcrypto import generate

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

def create_site(admin_pass: DeterministicKeyPassphrase, directory:str='.')->UserID:
    public_key, private_key = generate.generate_deterministic(admin_pass)

    raw_tar = io.BytesIO()

    tar = tarfile.open(mode='x:gz', fileobj=raw_tar)
    tar.add(directory)
    tar.close()

    raw_tar.seek(0)

    insert.insert(raw_tar.read())

    return public_key