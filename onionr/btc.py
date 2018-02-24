'''
    Onionr - P2P Microblogging Platform & Social network

    Handle bitcoin operations
'''
'''
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
'''
from bitpeer.node import *
from bitpeer.storage.shelve import ShelveStorage
import logging, time
import socks, sys
class OnionrBTC:
	def __init__(self, lastBlock='00000000000000000021ee6242d08e3797764c9258e54e686bc2afff51baf599', lastHeight=510613, torP=9050):
		stream = logging.StreamHandler()
		logger = logging.getLogger('halfnode')
		logger.addHandler(stream)
		logger.setLevel (10)

		LASTBLOCK = lastBlock
		LASTBLOCKINDEX = lastHeight
		self.node = Node ('BTC', ShelveStorage ('data/btc-blocks.db'), lastblockhash=LASTBLOCK, lastblockheight=LASTBLOCKINDEX, torPort=torP)

		self.node.bootstrap ()
		self.node.connect ()
		self.node.loop ()

