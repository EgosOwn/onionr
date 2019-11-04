import sys
import getpass

from httpapi import onionrsitesapi
import onionrexceptions
import logger
from etc import onionrvalues

def create_multipage_site():
    error_encountered = False
    try:
        directory = sys.argv[2]
    except IndexError:
        directory = '.'
    try:
        passphrase = sys.argv[3]
    except IndexError:
        logger.warn('''It is critical that this passphrase is long.
If you want to update your site later you must remember the passphrase.''', terminal=True)
        logger.info(f'Please enter a site passphrase of at least {onionrvalues.PASSWORD_LENGTH} characters.', terminal=True)
        passphrase = getpass.getpass()
        logger.info('Confirm:', terminal=True)
        confirm = getpass.getpass()
        if passphrase != confirm:
            logger.error('Passphrases do not match', terminal=True)
            error_encountered = True

    if len(passphrase) < onionrvalues.PASSWORD_LENGTH:
        error_encountered = True
        logger.error(f'Passphrase must be at least {onionrvalues.PASSWORD_LENGTH} characters.', terminal=True)

    if error_encountered: 
        sys.exit(1)

    results = onionrsitesapi.sitefiles.create_site(passphrase, directory=directory)
    results = (results[0].replace('=', ''), results[1])
    logger.info(f'Site address {results[0]}', terminal=True)
    logger.info(f'Block for this version {results[1]}', terminal=True)

create_multipage_site.onionr_help = "[directory path (default relative)] - packages a whole directory and makes it available as an Onionr site."
