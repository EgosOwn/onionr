'''
    Onionr - Private P2P Communication

    Select a random online peer in a communicator instance and have them "cool down"
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
def cooldown_peer(comm_inst):
    '''Randomly add an online peer to cooldown, so we can connect a new one'''
    onlinePeerAmount = len(comm_inst.onlinePeers)
    minTime = 300
    cooldownTime = 600
    toCool = ''
    tempConnectTimes = dict(comm_inst.connectTimes)

    # Remove peers from cooldown that have been there long enough
    tempCooldown = dict(comm_inst.cooldownPeer)
    for peer in tempCooldown:
        if (comm_inst._core._utils.getEpoch() - tempCooldown[peer]) >= cooldownTime:
            del comm_inst.cooldownPeer[peer]

    # Cool down a peer, if we have max connections alive for long enough
    if onlinePeerAmount >= comm_inst._core.config.get('peers.max_connect', 10, save = True):
        finding = True

        while finding:
            try:
                toCool = min(tempConnectTimes, key=tempConnectTimes.get)
                if (comm_inst._core._utils.getEpoch() - tempConnectTimes[toCool]) < minTime:
                    del tempConnectTimes[toCool]
                else:
                    finding = False
            except ValueError:
                break
        else:
            comm_inst.removeOnlinePeer(toCool)
            comm_inst.cooldownPeer[toCool] = comm_inst._core._utils.getEpoch()

    comm_inst.decrementThreadCount('cooldown_peer')