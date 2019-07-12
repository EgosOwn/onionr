'''
    Onionr - Private P2P Communication

    Return a reliability score sorted list of peers
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
def get_score_sorted_peer_list(coreInst):
    peer_list = coreInst.listAdders()
    peer_scores = {}
    peer_times = {}

    for address in peer_list:
        # Load peer's profiles into a list
        profile = PeerProfiles(address, coreInst)
        peer_scores[address] = profile.score
        if not isinstance(profile.connectTime, type(None)):
            peer_times[address] = profile.connectTime
        else:
            peer_times[address] = 9000

    # Sort peers by their score, greatest to least, and then last connected time
    peer_list = sorted(peer_scores, key=peer_scores.get, reverse=True)
    peer_list = sorted(peer_times, key=peer_times.get, reverse=True)
    return peer_list