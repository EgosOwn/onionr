'''
    Onionr - P2P Microblogging Platform & Social network

    This file defines values and requirements used by Onionr
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

class OnionrValues:
    def __init__(self):
        self.passwordLength = 20
        self.blockMetadataLengths = {'meta': 1000, 'sig': 200, 'signer': 200, 'time': 10, 'powRandomToken': 1000, 'encryptType': 4, 'expire': 14} #TODO properly refine values to minimum needed
        self.default_expire = 2592000