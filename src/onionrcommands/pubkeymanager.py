"""Onionr - Private P2P Communication.

This module defines user ID-related CLI commands
"""
import sys
import getpass

import unpaddedbase32
import niceware

import logger
import onionrexceptions
from onionrutils import stringvalidators, bytesconverter
import config
import keymanager
import onionrcrypto
import onionrvalues
"""
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
"""


DETERMINISTIC_REQUIREMENT = onionrvalues.PASSWORD_LENGTH


def add_ID():
    """Command to create a new user ID key pair."""
    key_manager = keymanager.KeyManager()
    pw = ""
    try:
        sys.argv[2]  # pylint: disable=W0104
        if not sys.argv[2].lower() == 'true':
            raise ValueError
    except (IndexError, ValueError):
        newID = key_manager.addKey()[0]
    else:
        pw = "-".join(niceware.generate_passphrase(32))
        newID, privKey = onionrcrypto.generate_deterministic(pw)
        try:
            key_manager.addKey(pubKey=newID,
                               privKey=privKey)
        except ValueError:
            logger.error(
                'That ID is already available, you can change to it ' +
                'with the change-id command.', terminal=True)
            return
    if pw:
        print("Phrase to restore ID:", pw)
    logger.info('Added ID: %s' %
                (bytesconverter.bytes_to_str(newID.replace('=', '')),), terminal=True)


add_ID.onionr_help = "If the first argument is true, "  # type: ignore
add_ID.onionr_help += "Onionr will show a deterministic "  # type: ignore
add_ID.onionr_help += "generation prompt. Otherwise it will "  # type: ignore
add_ID.onionr_help += "generate & save a new random key pair."  # type: ignore


def change_ID():
    """Command to change active ID from argv or stdin."""
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


change_ID.onionr_help = "<pubkey>: Switches Onionr to "  # type: ignore
change_ID.onionr_help += "use a different user ID key. "  # type: ignore
change_ID.onionr_help += "You should immediately restart "  # type: ignore
change_ID.onionr_help += "Onionr if it is running."  # type: ignore
