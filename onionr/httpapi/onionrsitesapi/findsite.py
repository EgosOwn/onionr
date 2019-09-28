import onionrexceptions
from onionrutils import mnemonickeys
from onionrutils import stringvalidators

def find_site(user_id: str)->str:
    if '-' in user_id: user_id = mnemonickeys.get_base32(user_id)
    if not stringvalidators.validate_pub_key(user_id): raise onionrexceptions.InvalidPubkey

    #for 
    