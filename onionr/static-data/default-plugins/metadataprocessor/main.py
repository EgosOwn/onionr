'''
    Onionr - P2P Anonymous Storage Network

    This processes metadata for Onionr blocks
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

# useful libraries
import logger, config
import os, sys, json, time, random, shutil, base64, getpass, datetime, re
from onionrblockapi import Block
import onionrusers, onionrexceptions

plugin_name = 'metadataprocessor'

# event listeners

def _processUserInfo(api, newBlock):
    '''
        Set the username for a particular user, from a signed block by them
    '''
    myBlock = newBlock
    peerName = myBlock.getMetadata('name')
    try:
        if len(peerName) > 20:
            raise onionrexceptions.InvalidMetdata('Peer name specified is too large')
    except TypeError:
        pass
    except onionrexceptions.InvalidMetadata:
        pass
    else:
        api.get_core().setPeerInfo(signer, 'name', peerName)
        logger.info('%s is now using the name %s.' % (signer, api.get_utils().escapeAnsi(peerName)))

def _processForwardKey(api, myBlock):
    '''
        Get the forward secrecy key specified by the user for us to use
    '''
    peer = onionrusers.OnionrUser(self.api.get_core(), myBlock.signer)
    key = myBlock.getMetadata('newFSKey')

    # We don't need to validate here probably, but it helps
    if api.get_utils().validatePubKey(key):
        peer.addForwardKey(key)
    else:
        raise onionrexceptions.InvalidPubkey("%s is nota valid pubkey key" % (key,))

def on_processBlocks(api):
    # Generally fired by utils.
    myBlock = api.data['block']
    blockType = api.data['type']
    logger.info('blockType is ' + blockType)

    # Process specific block types

    # userInfo blocks, such as for setting username
    if blockType == 'userInfo':
        if api.data['validSig'] == True: # we use == True for type safety
            _processUserInfo(api, myBlock)
    # forwardKey blocks, add a new forward secrecy key for a peer
    elif blockType == 'forwardKey':
        if api.data['validSig'] == True:
            _processForwardKey(api, myBlock)
    # socket blocks
    elif blockType == 'openSocket':
        if api.data['validSig'] == True and myBlock.decrypted: # we check if it is decrypted as a way of seeing if it was for us
            try:
                address = api.data['address']
            except KeyError:
                raise onionrexceptions.MissingAddress("Missing address for new socket")
            try:
                port = api.data['port']
            except KeyError:
                raise ValueError("Missing port for new socket")

            socketInfo = json.dumps({'peer': api.data['signer'], 'address': address, 'port': port, create = False})
            api.get_core().daemonQueueAdd('startSocket', socketInfo)

def on_init(api, data = None):

    pluginapi = api

    return
