'''
    Onionr - P2P Anonymous Storage Network

    Onionr Chat Messages
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
import logger
class OnionrChat:
    def __init__(self, coreInst):
        return
    
    def recieveMessage(self, socketInst, data):
        logger.info('Got %s' % (data,))
        return ''
    
    def sendMessage(self, socketInst, data):
        return "Hello"