'''
    Onionr - P2P Anonymous Storage Network

    This module serializes various data pieces for use in other modules, in particular the web api
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

import core, api, uuid, json

class SerializedData:
    def __init__(self, coreInst):
        '''
        Serialized data is in JSON format:
        {
            'success': bool,
            'foo': 'bar',
            etc
        }
        '''
        assert isinstance(coreInst, core.Core)
        self._core = coreInst
    
    def getStats(self):
        '''Return statistics about our node'''
        stats = {}
        stats['uptime'] = self._core.onionrInst.communicatorInst.getUptime()
        stats['connectedNodes'] = '\n'.join(self._core.onionrInst.communicatorInst.onlinePeers)
        stats['blockCount'] = len(self._core.getBlockList())
        stats['blockQueueCount'] = len(self._core.onionrInst.communicatorInst.blockQueue)
        return json.dumps(stats)
