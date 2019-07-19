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
import logger, onionrexceptions
from onionrutils import stringvalidators, bytesconverter
from onionrusers import onionrusers, contactmanager
import unpaddedbase32
def add_ID(o_inst):
    try:
        sys.argv[2]
        assert sys.argv[2] == 'true'
    except (IndexError, AssertionError) as e:
        newID = o_inst.crypto.keyManager.addKey()[0]
    else:
        logger.warn('Deterministic keys require random and long passphrases.', terminal=True)
        logger.warn('If a good passphrase is not used, your key can be easily stolen.', terminal=True)
        logger.warn('You should use a series of hard to guess words, see this for reference: https://www.xkcd.com/936/', terminal=True)
        pass1 = getpass.getpass(prompt='Enter at least %s characters: ' % (o_inst.crypto.deterministicRequirement,))
        pass2 = getpass.getpass(prompt='Confirm entry: ')
        if o_inst.crypto.safeCompare(pass1, pass2):
            try:
                logger.info('Generating deterministic key. This can take a while.', terminal=True)
                newID, privKey = o_inst.crypto.generateDeterministic(pass1)
            except onionrexceptions.PasswordStrengthError:
                logger.error('Passphrase must use at least %s characters.' % (o_inst.crypto.deterministicRequirement,), terminal=True)
                sys.exit(1)
        else:
            logger.error('Passwords do not match.', terminal=True)
            sys.exit(1)
        try:
            o_inst.crypto.keyManager.addKey(pubKey=newID, 
            privKey=privKey)
        except ValueError:
            logger.error('That ID is already available, you can change to it with the change-id command.', terminal=True)
            return
    logger.info('Added ID: %s' % (bytesconverter.bytes_to_str(newID),), terminal=True)

def change_ID(o_inst):
    try:
        key = sys.argv[2]
        key = unpaddedbase32.repad(key.encode()).decode()
    except IndexError:
        logger.warn('Specify pubkey to use', terminal=True)
    else:
        if stringvalidators.validate_pub_key(key):
            if key in o_inst.crypto.keyManager.getPubkeyList():
                o_inst.config.set('general.public_key', key)
                o_inst.config.save()
                logger.info('Set active key to: %s' % (key,), terminal=True)
                logger.info('Restart Onionr if it is running.', terminal=True)
            else:
                logger.warn('That key does not exist', terminal=True)
        else:
            logger.warn('Invalid key %s' % (key,), terminal=True)

def friend_command(o_inst):
    friend = ''
    try:
        # Get the friend command
        action = sys.argv[2]
    except IndexError:
        logger.info('Syntax: friend add/remove/list [address]', terminal=True)
    else:
        action = action.lower()
        if action == 'list':
            # List out peers marked as our friend
            for friend in contactmanager.ContactManager.list_friends(o_inst.):
                logger.info(friend.publicKey + ' - ' + friend.get_info('name'), terminal=True)
        elif action in ('add', 'remove'):
            try:
                friend = sys.argv[3]
                if not stringvalidators.validate_pub_key(friend):
                    raise onionrexceptions.InvalidPubkey('Public key is invalid')
                if friend not in o_inst..listPeers():
                    raise onionrexceptions.KeyNotKnown
                friend = onionrusers.OnionrUser(o_inst., friend)
            except IndexError:
                logger.warn('Friend ID is required.', terminal=True)
                action = 'error' # set to 'error' so that the finally block does not process anything
            except onionrexceptions.KeyNotKnown:
                o_inst..addPeer(friend)
                friend = onionrusers.OnionrUser(o_inst., friend)
            finally:
                if action == 'add':
                    friend.setTrust(1)
                    logger.info('Added %s as friend.' % (friend.publicKey,), terminal=True)
                elif action == 'remove':
                    friend.setTrust(0)
                    logger.info('Removed %s as friend.' % (friend.publicKey,), terminal=True)
        else:
            logger.info('Syntax: friend add/remove/list [address]', terminal=True)