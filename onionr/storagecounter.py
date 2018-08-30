'''
    Onionr - P2P Microblogging Platform & Social network.

    Keeps track of how much disk space we're using
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
import config

class StorageCounter:
    def __init__(self, coreInst):
        self._core = coreInst
        self.dataFile = self._core.usageFile
        return

    def isFull(self):
        retData = False
        if self._core.config.get('allocations.disk') <= (self.getAmount() + 1000):
            retData = True
        return retData

    def _update(self, data):
        with open(self.dataFile, 'w') as dataFile:
            dataFile.write(str(data))
    def getAmount(self):
        '''Return how much disk space we're using (according to record)'''
        retData = 0
        try:
            with open(self.dataFile, 'r') as dataFile:
                retData = int(dataFile.read())
        except FileNotFoundError:
            pass
        return retData

    def addBytes(self, amount):
        '''Record that we are now using more disk space, unless doing so would exceed configured max'''
        newAmount = amount + self.getAmount()
        retData = newAmount
        if newAmount > self._core.config.get('allocations.disk'):
            retData = False
        else:
            self._update(newAmount)
        return retData

    def removeBytes(self, amount):
        '''Record that we are now using less disk space'''
        newAmount = self.getAmount() - amount
        self._update(newAmount)
        return newAmount