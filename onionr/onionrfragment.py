'''
    Onionr - P2P Anonymous Storage Network

    This file contains the OnionrFragment class which implements the fragment system
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

# onionr:10ch+10ch+10chgdecryptionkey
import core, sys, binascii, os

FRAGMENT_SIZE = 0.25
TRUNCATE_LENGTH = 30

class OnionrFragment:
    def __init__(self, uri=None):
        uri = uri.replace('onionr:', '')
        count = 0
        blocks = []
        appendData = ''
        key = ''
        for x in uri:
            if x == 'k':
                key = uri[uri.index('k') + 1:]
            appendData += x
            if count == TRUNCATE_LENGTH:
                blocks.append(appendData)
                appendData = ''
                count = 0
            count += 1
        self.key = key
        self.blocks = blocks
        return

    @staticmethod
    def generateFragments(data=None, coreInst=None):
        if coreInst is None:
            coreInst = core.Core()

        key = os.urandom(32)
        data = coreInst._crypto.symmetricEncrypt(data, key).decode()
        blocks = []
        blockData = b""
        uri = "onionr:"
        total = sys.getsizeof(data)
        for x in data:
            blockData += x.encode()
            if round(len(blockData) / len(data), 3) > FRAGMENT_SIZE:
                blocks.append(core.Core().insertBlock(blockData))
                blockData = b""

        for bl in blocks:
            uri += bl[:TRUNCATE_LENGTH]
        uri += "k"
        uri += binascii.hexlify(key).decode()
        return (uri, key)

if __name__ == '__main__':
    uri = OnionrFragment.generateFragments("test")[0]
    print(uri)
    OnionrFragment(uri)