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
    def __init__(self, communicatorInst):
        '''OnionrChat uses onionrsockets (handled by the communicator) to exchange direct chat messages'''
        self.communicator = communicatorInst
        self._core = self.communicator._core
        self._utils = self._core._utils

        self.chats = {} # {'peer': {'date': date, message': message}}
        self.chatSend = {}

    def chatHandler(self):
        while not self.communicator.shutdown:
            for peer in self._core.socketServerConnData:
                try:
                    assert self._core.socketReasons[peer] == "chat"
                except (AssertionError, KeyError) as e:
                    logger.warn('Peer is not for chat')
                    continue
                else:
                    self.chats[peer] = {'date': self._core.socketServerConnData[peer]['date'], 'data': self._core.socketServerConnData[peer]['data']}
                    logger.info("CHAT MESSAGE RECIEVED: %s" % self.chats[peer]['data'])
            for peer in self.communicator.socketClient.sockets:
                try:
                    logger.info(self.communicator.socketClient.connPool[peer]['data'])
                    self.communicator.socketClient.sendData(peer, "lol")
                except:
                    pass
            time.sleep(2)