'''
    Onionr - Private P2P Communication

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
import config, filepaths
config.reload()
class StorageCounter:
    def __init__(self):
        self.dataFile = filepaths.usage_file
        return

    def isFull(self):
        retData = False
        if config.get('allocations.disk', 2000000000) <= (self.getAmount() + 1000):
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
        except ValueError:
            pass # Possibly happens when the file is empty
        return retData
    
    def getPercent(self):
        '''Return percent (decimal/float) of disk space we're using'''
        amount = self.getAmount()
        return round(amount / config.get('allocations.disk', 2000000000), 2)

    def addBytes(self, amount):
        '''Record that we are now using more disk space, unless doing so would exceed configured max'''
        newAmount = amount + self.getAmount()
        retData = newAmount
        if newAmount > config.get('allocations.disk', 2000000000):
            retData = False
        else:
            self._update(newAmount)
        return retData

    def removeBytes(self, amount):
        '''Record that we are now using less disk space'''
        newAmount = self.getAmount() - amount
        self._update(newAmount)
        return newAmount