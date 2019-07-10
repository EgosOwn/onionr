'''
    Onionr - Private P2P Communication

    interact with the peer pool in a communicator instance
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

from . import clearofflinepeer, onlinepeers, pickonlinepeers

clear_offline_peer = clearofflinepeer.clear_offline_peer
get_online_peers = onlinepeers.get_online_peers
pick_online_peer = pickonlinepeers.pick_online_peer