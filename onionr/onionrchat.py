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
import logger, time
class OnionrChat:
    def __init__(self, communicatorInst, socketInst):
        self.communicator = communicatorInst
        self.socket = socketInst

        while True:
            time.sleep(2)
            logger.info(self.socket.readData())
            self.socket.sendData('rekt')
        return