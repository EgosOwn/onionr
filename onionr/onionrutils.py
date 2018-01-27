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
import getpass, sys, requests, configparser, os, socket, gnupg, hashlib, logger
if sys.version_info < (3, 6):
    try:
        import sha3
    except ModuleNotFoundError:
        logger.fatal('On Python 3 versions prior to 3.6.x, you need the sha3 module')
        sys.exit(1)
class OnionrUtils:
    '''Various useful functions'''
    def __init__(self, coreInstance):
        self.fingerprintFile = 'data/own-fingerprint.txt'
        self._core = coreInstance
        return
    def printErr(self, text='an error occured'):
        '''Print an error message to stderr with a new line'''
        logger.error(text)
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
                logger.error("Passwords do not match.")
                input()
            else:
                break
        return pass1
    def checkPort(self, port):
        '''Checks if a port is available, returns bool'''
        # inspired by https://www.reddit.com/r/learnpython/comments/2i4qrj/how_to_write_a_python_script_that_checks_to_see/ckzarux/
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        retVal = False
        try:
            sock.bind(('', port))
        except OSError as e:
            if e.errno is 98:
                retVal = True
        finally:
            sock.close()
        return retVal
    def checkIsIP(self, ip):
        try:
            socket.inet_aton(ip)
        except:
            return False
        else:
            return True
    def exportMyPubkey(self):
        '''Export our PGP key if it exists'''
        if not os.path.exists(self.fingerprintFile):
            raise Exception("No fingerprint found, cannot export our PGP key.")
        if os.getenv('TRAVIS') == 'true':
            gpg = gnupg.GPG(homedir='./data/pgp/')
        else:
            gpg = gnupg.GPG(gnupghome='./data/pgp/')
        with open(self.fingerprintFile,'r') as f:
            fingerprint = f.read()
        ascii_armored_public_keys = gpg.export_keys(fingerprint)
        return ascii_armored_public_keys

    def getBlockDBHash(self):
        '''Return a sha3_256 hash of the blocks DB'''
        with open(self._core.blockDB, 'rb') as data:
            data = data.read()
        hasher = hashlib.sha3_256()
        hasher.update(data)
        dataHash = hasher.hexdigest()
        return dataHash

    def validateHash(self, data, length=64):
        '''validate if a string is a valid hex formatted hash'''
        retVal = True
        if len(data) != length:
            retVal = False
        else:
            try:
                int(data, 16)
            except ValueError:
                retVal = False
        return retVal
    def validateID(self, id):
        '''validate if a user ID is a valid tor or i2p hidden service'''
        idLength = len(id)
        retVal = True
        idNoDomain = ''
        peerType = ''
        # i2p b32 addresses are 60 characters long (including .b32.i2p)
        if idLength == 60:
            peerType = 'i2p'
            if not id.endswith('.b32.i2p'):
                retVal = False
            else:
                idNoDomain = id.split('.b32.i2p')[0]
        # Onion v2's are 22 (including .onion), v3's are 62 with .onion
        elif idLength == 22 or idLength == 62:
            peerType = 'onion'
            if not id.endswith('.onion'):
                retVal = False
            else:
                idNoDomain = id.split('.onion')[0]
        else:
            retVal = False
        if retVal:
            if peerType == 'i2p':
                try:
                    id.split('.b32.i2p')[2]
                except:
                    pass
                else:
                    retVal = False
            elif peerType == 'onion':
                try:
                    id.split('.onion')[2]
                except:
                    pass
                else:
                    retVal = False
            if not idNoDomain.isalnum():
                retVal = False
        return retVal

