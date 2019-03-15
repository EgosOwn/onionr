'''
    Onionr - P2P Anonymous Storage Network

    This module defines ID-related CLI commands
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
import logger
from onionrusers import onionrusers
def add_ID(o_inst):
    try:
        sys.argv[2]
        assert sys.argv[2] == 'true'
    except (IndexError, AssertionError) as e:
        newID = o_inst.onionrCore._crypto.keyManager.addKey()[0]
    else:
        logger.warn('Deterministic keys require random and long passphrases.')
        logger.warn('If a good passphrase is not used, your key can be easily stolen.')
        logger.warn('You should use a series of hard to guess words, see this for reference: https://www.xkcd.com/936/')
        pass1 = getpass.getpass(prompt='Enter at least %s characters: ' % (o_inst.onionrCore._crypto.deterministicRequirement,))
        pass2 = getpass.getpass(prompt='Confirm entry: ')
        if o_inst.onionrCore._crypto.safeCompare(pass1, pass2):
            try:
                logger.info('Generating deterministic key. This can take a while.')
                newID, privKey = o_inst.onionrCore._crypto.generateDeterministic(pass1)
            except onionrexceptions.PasswordStrengthError:
                logger.error('Must use at least 25 characters.')
                sys.exit(1)
        else:
            logger.error('Passwords do not match.')
            sys.exit(1)
        o_inst.onionrCore._crypto.keyManager.addKey(pubKey=newID, 
        privKey=privKey)
    logger.info('Added ID: %s' % (o_inst.onionrUtils.bytesToStr(newID),))

def change_ID(o_inst):
    try:
        key = sys.argv[2]
    except IndexError:
        logger.error('Specify pubkey to use')
    else:
        if o_inst.onionrUtils.validatePubKey(key):
            if key in o_inst.onionrCore._crypto.keyManager.getPubkeyList():
                o_inst.onionrCore.config.set('general.public_key', key)
                o_inst.onionrCore.config.save()
                logger.info('Set active key to: %s' % (key,))
                logger.info('Restart Onionr if it is running.')
            else:
                logger.error('That key does not exist')
        else:
            logger.error('Invalid key %s' % (key,))

def friend_command(o_inst):
    friend = ''
    try:
        # Get the friend command
        action = sys.argv[2]
    except IndexError:
        logger.info('Syntax: friend add/remove/list [address]')
    else:
        action = action.lower()
        if action == 'list':
            # List out peers marked as our friend
            for friend in onionrusers.OnionrUser.list_friends(o_inst.onionrCore):
                logger.info(friend.publicKey + ' - ' + friend.getName())
        elif action in ('add', 'remove'):
            try:
                friend = sys.argv[3]
                if not o_inst.onionrUtils.validatePubKey(friend):
                    raise onionrexceptions.InvalidPubkey('Public key is invalid')
                if friend not in o_inst.onionrCore.listPeers():
                    raise onionrexceptions.KeyNotKnown
                friend = onionrusers.OnionrUser(o_inst.onionrCore, friend)
            except IndexError:
                logger.error('Friend ID is required.')
            except onionrexceptions.KeyNotKnown:
                o_inst.onionrCore.addPeer(friend)
                friend = onionrusers.OnionrUser(o_inst.onionrCore, friend)
            finally:
                if action == 'add':
                    friend.setTrust(1)
                    logger.info('Added %s as friend.' % (friend.publicKey,))
                else:
                    friend.setTrust(0)
                    logger.info('Removed %s as friend.' % (friend.publicKey,))
        else:
            logger.info('Syntax: friend add/remove/list [address]')