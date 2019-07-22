'''
    Onionr - Private P2P Communication

    Get floored epoch, or rounded epoch
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
import math, time
def get_rounded_epoch(roundS=60):
    '''
        Returns the epoch, rounded down to given seconds (Default 60)
    '''
    epoch = get_epoch()
    return epoch - (epoch % roundS)

def get_epoch():
    '''returns epoch'''
    return math.floor(time.time())