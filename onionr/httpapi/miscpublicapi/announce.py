'''
    Onionr - Private P2P Communication

    Handle announcements to the public API server
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
import base64
from flask import Response
import logger
from etc import onionrvalues
from onionrutils import stringvalidators, bytesconverter

def handle_announce(clientAPI, request):
    '''
    accept announcement posts, validating POW
    clientAPI should be an instance of the clientAPI server running, request is a instance of a flask request
    '''
    resp = 'failure'
    powHash = ''
    randomData = ''
    newNode = ''
    ourAdder = clientAPI.hsAddress.encode()
    try:
        newNode = request.form['node'].encode()
    except KeyError:
        logger.warn('No node specified for upload')
        pass
    else:
        try:
            randomData = request.form['random']
            randomData = base64.b64decode(randomData)
        except KeyError:
            logger.warn('No random data specified for upload')
        else:
            nodes = newNode + clientAPI.hsAddress.encode()
            nodes = clientAPI.crypto.blake2bHash(nodes)
            powHash = clientAPI.crypto.blake2bHash(randomData + nodes)
            try:
                powHash = powHash.decode()
            except AttributeError:
                pass
            if powHash.startswith('0' * onionrvalues.OnionrValues().announce_pow):
                newNode = bytesconverter.bytes_to_str(newNode)
                if stringvalidators.validate_transport(newNode) and not newNode in clientAPI.onionrInst.communicatorInst.newPeers:
                    clientAPI.onionrInst.communicatorInst.newPeers.append(newNode)
                    resp = 'Success'
            else:
                logger.warn(newNode.decode() + ' failed to meet POW: ' + powHash)
    resp = Response(resp)
    if resp == 'failure':
        return resp, 406
    return resp