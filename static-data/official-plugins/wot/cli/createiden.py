import base64

import keyring.errors
from nacl.signing import SigningKey

from logger import log as logging
import config

from wot import wotkeyring
from wot.identity import Identity

def create_new_iden():
    iden = Identity(
        SigningKey.generate(),
        input('Enter a name for your identity: '))
    try:
        wotkeyring.set_identity(iden)
    except keyring.errors.NoKeyringError:
        logging.warn(
            "Could not use secure keyring to store your WOT " +
            "private key, using config.")
        logging.info("Using config file to store identity private key")
        config.set(
            'wot.identity.{iden.name}',
            base64.b85encode(
                bytes(iden.private_key)).decode('utf-8'), savefile=True)
    config.set(
        'wot.active_identity_name', iden.name, savefile=True)
    logging.info(
        'Identity created and automatically set as active. ' +
        'Restart Onionr to use it.')
