'''
    Onionr - Private P2P Communication

    Detect if Python is being run in optimized mode or not, which has security considerations for assert statements
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

def detect_optimization():
    '''Returns true if Python is run in optimized mode (-o), based on optimization ignoring assert statements'''
    try:
        assert True is False
    except AssertionError:
        return False
    return True