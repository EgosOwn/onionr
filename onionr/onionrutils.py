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
import getpass, sys, requests, os, socket, hashlib, logger, sqlite3, config, binascii
import nacl.signing, nacl.encoding

if sys.version_info < (3, 6):
    try:
        import sha3
    except ModuleNotFoundError:
        logger.fatal('On Python 3 versions prior to 3.6.x, you need the sha3 module')
        sys.exit(1)

class OnionrUtils:
    '''
        Various useful function
    '''
    def __init__(self, coreInstance):
        self.fingerprintFile = 'data/own-fingerprint.txt'
        self._core = coreInstance
        return

    def sendPM(self, user, message):
        '''High level function to encrypt a message to a peer and insert it as a block'''
        return
    
    def incrementAddressSuccess(self, address):
        '''Increase the recorded sucesses for an address'''
        increment = self._core.getAddressInfo(address, 'success') + 1
        self._core.setAddressInfo(address, 'success', increment)
        return
        
    def decrementAddressSuccess(self, address):
        '''Decrease the recorded sucesses for an address'''
        increment = self._core.getAddressInfo(address, 'success') - 1
        self._core.setAddressInfo(address, 'success', increment)
        return

    def mergeKeys(self, newKeyList):
        '''Merge ed25519 key list to our database'''
        retVal = False
        if newKeyList != False:
            for key in newKeyList:
                if not key in self._core.listPeers(randomOrder=False):
                    if self._core.addPeer(key):
                        retVal = True
        return retVal

    
    def mergeAdders(self, newAdderList):
        '''Merge peer adders list to our database'''
        retVal = False
        if newAdderList != False:
            for adder in newAdderList:
                if not adder in self._core.listAdders(randomOrder=False):
                    if self._core.addAddress(adder):
                        retVal = True
        return retVal

    def localCommand(self, command):
        '''
            Send a command to the local http API server, securely. Intended for local clients, DO NOT USE for remote peers.
        '''

        config.reload()

        # TODO: URL encode parameters, just as an extra measure. May not be needed, but should be added regardless.
        requests.get('http://' + open('data/host.txt', 'r').read() + ':' + str(config.get('client')['port']) + '/client/?action=' + command + '&token=' + str(config.get('client')['client_hmac']))

        return

    def getPassword(self, message='Enter password: ', confirm = True):
        '''
            Get a password without showing the users typing and confirm the input
        '''
        # Get a password safely with confirmation and return it
        while True:
            print(message)
            pass1 = getpass.getpass()
            if confirm:
                print('Confirm password: ')
                pass2 = getpass.getpass()
                if pass1 != pass2:
                    logger.error("Passwords do not match.")
                    logger.readline()
                else:
                    break
            else:
                break

        return pass1

    def checkPort(self, port, host=''):
        '''
            Checks if a port is available, returns bool
        '''
        # inspired by https://www.reddit.com/r/learnpython/comments/2i4qrj/how_to_write_a_python_script_that_checks_to_see/ckzarux/
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        retVal = False
        try:
            sock.bind((host, port))
        except OSError as e:
            if e.errno is 98:
                retVal = True
        finally:
            sock.close()

        return retVal

    def checkIsIP(self, ip):
        '''
            Check if a string is a valid IPv4 address
        '''
        try:
            socket.inet_aton(ip)
        except:
            return False
        else:
            return True

    def getBlockDBHash(self):
        '''
            Return a sha3_256 hash of the blocks DB
        '''
        with open(self._core.blockDB, 'rb') as data:
            data = data.read()
        hasher = hashlib.sha3_256()
        hasher.update(data)
        dataHash = hasher.hexdigest()

        return dataHash

    def hasBlock(self, hash):
        '''
            Check for new block in the list
        '''
        conn = sqlite3.connect(self._core.blockDB)
        c = conn.cursor()
        if not self.validateHash(hash):
            raise Exception("Invalid hash")
        for result in c.execute("SELECT COUNT() FROM hashes where hash='" + hash + "'"):
            if result[0] >= 1:
                conn.commit()
                conn.close()
                return True
            else:
                conn.commit()
                conn.close()
                return False

    def validateHash(self, data, length=64):
        '''
            Validate if a string is a valid hex formatted hash
        '''
        retVal = True
        if data == False or data == True:
            return False
        data = data.strip()
        if len(data) != length:
            retVal = False
        else:
            try:
                int(data, 16)
            except ValueError:
                retVal = False

        return retVal

    def validatePubKey(self, key):
        '''Validate if a string is a valid base32 encoded Ed25519 key'''
        retVal = False
        try:
            nacl.signing.SigningKey(seed=key, encoder=nacl.encoding.Base32Encoder)
        except nacl.exceptions.ValueError:
            pass
        except binascii.Error:
            pass
        else:
            retVal = True
        return retVal


    def validateID(self, id):
        '''
            Validate if an address is a valid tor or i2p hidden service
        '''
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
