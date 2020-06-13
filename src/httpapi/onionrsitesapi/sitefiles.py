"""Onionr - Private P2P Communication.

Read onionr site files
"""
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
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


def find_site_gzip(user_id: str)->tarfile.TarFile:
    """Return verified site tar object"""
    sites = blockmetadb.get_blocks_by_type('osite')
    user_site = None
    unpadded_user = user_id
    user_id = unpaddedbase32.repad(user_id)
    for site in sites:
        block = onionrblockapi.Block(site)
        if block.isSigner(user_id) or block.isSigner(unpadded_user):
            user_site = block
    if not user_site is None:
        return tarfile.open(fileobj=io.BytesIO(user_site.bcontent), mode='r')
    return None


def get_file(user_id, file)->Union[bytes, None]:
    """Get a site file content"""
    ret_data = ""
    site = find_site_gzip(user_id)

    if file.endswith('/'):
        file += 'index.html'
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
