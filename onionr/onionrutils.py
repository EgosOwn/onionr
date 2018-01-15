'''
    Onionr - P2P Microblogging Platform & Social network

    OnionrUtils offers various useful functions to Onionr. Relatively misc.
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
# Misc functions that do not fit in the main api, but are useful
import getpass, sys, requests, configparser, os
class OnionrUtils():
    '''Various useful functions'''
    def __init__(self):
        return
    def printErr(self, text='an error occured'):
        '''Print an error message to stderr with a new line'''
        sys.stderr.write(text + '\n')
    def localCommand(self, command):
        '''Send a command to the local http API server, securely. Intended for local clients, DO NOT USE for remote peers.'''
        config = configparser.ConfigParser()
        if os.path.exists('data/config.ini'):
            config.read('data/config.ini')
        else:
            return
        requests.get('http://' + open('data/host.txt', 'r').read() + ':' + str(config['CLIENT']['PORT']) + '/client/?action=' + command + '&token=' + config['CLIENT']['CLIENT HMAC'])
    def getPassword(self, message='Enter password: '):
        '''Get a password without showing the users typing and confirm the input'''
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