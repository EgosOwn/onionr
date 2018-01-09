'''
    Onionr - P2P Microblogging Platform & Social network
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
# Misc functions that do not fit in the main api, but are useful
import getpass
class OnionrUtils():
    def __init__(self):
        return
    def getPassword(self, message='Enter password: '):
        # Get a password safely with confirmation and return it
        while True:
            print(message)
            pass1 = getpass.getpass()
            print('Confirm password: ')
            pass2 = getpass.getpass()
            if pass1 != pass2:
                print("Passwords do not match.")
                input()
            else:
                break
        return pass1