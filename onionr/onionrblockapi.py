'''
    Onionr - P2P Microblogging Platform & Social network.

    This class contains the OnionrBlocks class which is a class for working with Onionr blocks
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

import core as onionrcore

class Block:
    def __init__(self, hash = None, core = None):
        self.hash = hash
        self.core = core

        if self.getCore() is None:
            self.core = onionrcore.Core()
        if not self.getHash() is None:
            self.update()

    # logic

    def update(self, data = None, file = None):
        '''
            Loads data from a block in to the current object.

            Inputs:
            - data (str):
              - if None: will load from file by hash
              - else: will load from `data` string
            - file (str):
              - if None: will load from file specified in this parameter
              - else: will load from wherever block is stored by hash

            Outputs:
            - (bool): indicates whether or not the operation was successful
        '''

        return False

    def delete(self):
        return False

    def save(self):
        return False

    # getters

    def getHash(self):
        return self.hash

    def getCore(self):
        return self.core

    def getType(self):
        return self.btype

    def getMetadata(self):
        return self.bmetadata

    def getContent(self):
        return self.bcontent

    def getDate(self):
        return self.date

    def isValid(self):
        return self.valid

    def isSigned(self):
        return self.signed

    def getSigner(self):
        return self.signer

    # setters

    def setType(self, btype):
        self.btype = btype
        return self

    def setContent(self, bcontent):
        self.bcontent = bcontent
        return self

    # static

    ORDER_DATE = 0
    ORDER_ALPHABETIC = 1

    def getBlocks(type = None, signer = None, order = ORDER_DATE, reverse = False):
        return None

    def exists(hash):
        return None
