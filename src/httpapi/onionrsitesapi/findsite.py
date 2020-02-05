"""
    Onionr - Private P2P Communication

    view and interact with onionr sites
"""

from typing import Union

import onionrexceptions
from onionrutils import mnemonickeys
from onionrutils import stringvalidators
from coredb import blockmetadb
from onionrblocks.onionrblockapi import Block
from onionrtypes import BlockHash

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


def find_site(user_id: str) -> Union[BlockHash, None]:
    """Returns block hash str for latest block for a site by a given user id"""
    # If mnemonic delim in key, convert to base32 version
    if mnemonickeys.DELIMITER in user_id:
        user_id = mnemonickeys.get_base32(user_id)

    if not stringvalidators.validate_pub_key(user_id):
        raise onionrexceptions.InvalidPubkey

    found_site = None
    sites = blockmetadb.get_blocks_by_type('osite')

    # Find site by searching all site blocks. eww O(N) ☹️, TODO: event based
    for site in sites:
        site = Block(site)
        if site.isSigner(user_id) and site.verifySig():
            found_site = site.hash
    return found_site
