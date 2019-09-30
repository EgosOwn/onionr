'''
    Onionr - Private P2P Communication

    This module defines user ID-related CLI commands
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

import sys, getpass

import unpaddedbase32
import niceware

import vanityonionr
import logger, onionrexceptions
from onionrutils import stringvalidators, bytesconverter
from onionrusers import onionrusers, contactmanager
import config
from coredb import keydb
import keymanager, onionrcrypto
from etc import onionrvalues

DETERMINISTIC_REQUIREMENT = onionrvalues.PASSWORD_LENGTH
def add_ID():
    key_manager = keymanager.KeyManager()
    try:
        sys.argv[2]
        if not sys.argv[2].lower() == 'true': raise ValueError
    except (IndexError, ValueError) as e:
        newID = key_manager.addKey()[0]
    else:
        logger.warn('Deterministic keys require random and long passphrases.', terminal=True)
        logger.warn('If a good passphrase is not used, your key can be easily stolen.', terminal=True)
        logger.warn('You should use a series of hard to guess words, see this for reference: https://www.xkcd.com/936/', terminal=True)
        try:
            pass1 = getpass.getpass(prompt='Enter at least %s characters: ' % (DETERMINISTIC_REQUIREMENT,))
            pass2 = getpass.getpass(prompt='Confirm entry: ')
        except KeyboardInterrupt:
            sys.exit(42)
        if onionrcrypto.cryptoutils.safe_compare(pass1, pass2):
            try:
                logger.info('Generating deterministic key. This can take a while.', terminal=True)
                newID, privKey = onionrcrypto.generate_deterministic(pass1)
            except onionrexceptions.PasswordStrengthError:
                logger.error('Passphrase must use at least %s characters.' % (DETERMINISTIC_REQUIREMENT,), terminal=True)
                sys.exit(1)
        else:
            logger.error('Passwords do not match.', terminal=True)
            sys.exit(1)
        try:
            key_manager.addKey(pubKey=newID, 
            privKey=privKey)
        except ValueError:
            logger.error('That ID is already available, you can change to it with the change-id command.', terminal=True)
            return
    logger.info('Added ID: %s' % (bytesconverter.bytes_to_str(newID),), terminal=True)

add_ID.onionr_help = "If the first argument is true, Onionr will show a deterministic generation prompt. Otherwise it will generate & save a new random key pair."

def change_ID():
    key_manager = keymanager.KeyManager()
    try:
        key = sys.argv[2]
        key = unpaddedbase32.repad(key.encode()).decode()
    except IndexError:
        logger.warn('Specify pubkey to use', terminal=True)
    else:
        if stringvalidators.validate_pub_key(key):
            key_list = key_manager.getPubkeyList()
            if key in key_list or key.replace('=', '') in key_list:
                config.set('general.public_key', key)
                config.save()
                logger.info('Set active key to: %s' % (key,), terminal=True)
                logger.info('Restart Onionr if it is running.', terminal=True)
            else:
                logger.warn('That key does not exist', terminal=True)
        else:
            logger.warn('Invalid key %s' % (key,), terminal=True)

change_ID.onionr_help = "<pubkey>: Switches Onionr to use a different user ID key. You should immediately restart Onionr if it is running."

def add_vanity():
    key_manager = keymanager.KeyManager()
    tell = lambda tell: logger.info(tell, terminal=True)
    words = ''
    length = len(sys.argv) - 2
    if length == 0: return
    for i in range(2, len(sys.argv)):
        words += ' '
        words += sys.argv[i]
    try:
        if length == 1:
            tell('Finding vanity, this should only take a few moments.')
        else:
            tell('Finding vanity, this will probably take a really long time.')
        try:
            vanity = vanityonionr.find_multiprocess(words)
        except ValueError:
            logger.warn('Vanity words must be valid english bip39', terminal=True)
        else:
            b32_pub = unpaddedbase32.b32encode(vanity[0])
            tell('Found vanity address:\n' + niceware.bytes_to_passphrase(vanity[0]))
            tell('Base32 Public key: %s' % (b32_pub.decode(),))
            key_manager.addKey(b32_pub, unpaddedbase32.b32encode(vanity[1]))
    except KeyboardInterrupt:
        pass
add_vanity.onionr_help = "<space separated bip32 words> - Generates and stores an Onionr vanity address (see https://github.com/trezor/python-mnemonic/blob/master/mnemonic/wordlist/english.txt)"
