'''
    Onionr - P2P Microblogging Platform & Social network

    This default plugin allows users to encrypt/decrypt messages without using blocks
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

# Imports some useful libraries
import logger, config, threading, time, readline, datetime, sys, json
from onionrblockapi import Block
import onionrexceptions, onionrusers
import locale
locale.setlocale(locale.LC_ALL, '')

class PlainEncryption:
    def __init__(self, api):
        self.api = api
        return
    def encrypt(self):
        # peer, data
        plaintext = ""
        encrypted = ""
        # detect if signing is enabled
        sign = True
        try:
            if sys.argv[3].lower() == 'false':
                sign = False
        except IndexError:
            pass

        try:
            if not self.api.get_core()._utils.validatePubKey(sys.argv[2]):
                raise onionrexceptions.InvalidPubkey
        except (ValueError, IndexError) as e:
            logger.error("Peer public key not specified")
        except onionrexceptions.InvalidPubkey:
            logger.error("Invalid public key")
        else:
            pubkey = sys.argv[2]
            # Encrypt if public key is valid
            logger.info("Please enter your message (ctrl-d or -q to stop):")
            try:
                for line in sys.stdin:
                    if line == '-q\n':
                        break
                    plaintext += line
            except KeyboardInterrupt:
                sys.exit(1)
            # Build Message to encrypt
            data = {}
            myPub = self.api.get_core()._crypto.pubKey
            if sign:
                data['sig'] = self.api.get_core()._crypto.edSign(plaintext, key=self.api.get_core()._crypto.privKey, encodeResult=True)
                data['sig'] = self.api.get_core()._utils.bytesToStr(data['sig'])
                data['signer'] = myPub
            data['data'] = plaintext
            data = json.dumps(data)
            plaintext = data
            encrypted = self.api.get_core()._crypto.pubKeyEncrypt(plaintext, pubkey, anonymous=True, encodedData=True)
            encrypted = self.api.get_core()._utils.bytesToStr(encrypted)
            print('ONIONR ENCRYPTED DATA %s END ENCRYPTED DATA' % (encrypted,))
    def decrypt(self, data):
        plaintext = ""
        encrypted = data
        
        return
    

def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    pluginapi = api
    encrypt = PlainEncryption(pluginapi)
    api.commands.register(['encrypt'], encrypt.encrypt)
    api.commands.register(['decrypt'], encrypt.decrypt)
    return