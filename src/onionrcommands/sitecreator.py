"""Onionr - Private P2P Communication.

Command to create Onionr mutli-page sites
"""
import sys
import os
import getpass

from niceware import generate_passphrase

from httpapi import onionrsitesapi
import logger
from etc import onionrvalues
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


def create_multipage_site():
    """Command to create mutlipage sites with specified dir and password."""
    error_encountered = False
    orig_dir = os.getcwd()
    try:
        directory = sys.argv[2]
        os.chdir(directory)
        directory = '.'
    except IndexError:
        directory = '.'
    try:
        passphrase = sys.argv[3]
    except IndexError:
        logger.warn('''It is critical that this passphrase is long.
If you want to update your site later you must remember the passphrase.''',
                    terminal=True)

        passphrase = "-".join(generate_passphrase(32))
        print("Site restore phrase:", passphrase)

    if len(passphrase) < onionrvalues.PASSWORD_LENGTH:
        error_encountered = True
        logger.error(
            f'Passphrase must be at least {onionrvalues.PASSWORD_LENGTH}' +
            ' characters.', terminal=True)

    if error_encountered:
        sys.exit(1)
    logger.info('Generating site...', terminal=True)
    results = onionrsitesapi.sitefiles.create_site(
        passphrase, directory=directory)
    results = (results[0].replace('=', ''), results[1])
    logger.info(f'Site address {results[0]}', terminal=True)
    logger.info(f'Block for this version {results[1]}', terminal=True)
    os.chdir(orig_dir)


create_multipage_site.onionr_help = "[directory path "  # type: ignore
create_multipage_site.onionr_help += "(default relative)] "  # type: ignore
create_multipage_site.onionr_help += "- packages a whole "  # type: ignore
create_multipage_site.onionr_help += "directory and makes "  # type: ignore
create_multipage_site.onionr_help += "it available as "  # type: ignore
create_multipage_site.onionr_help += "an Onionr site."  # type: ignore
