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

def _processForwardKey(api, myBlock):
    '''
        Get the forward secrecy key specified by the user for us to use
    '''
    peer = onionrusers.OnionrUser(api.get_core(), myBlock.signer)
    key = myBlock.getMetadata('newFSKey')

    # We don't need to validate here probably, but it helps
    if api.get_utils().validatePubKey(key):
        peer.addForwardKey(key)
    else:
        raise onionrexceptions.InvalidPubkey("%s is nota valid pubkey key" % (key,))

def on_processblocks(api, data=None):
    # Generally fired by utils.
    myBlock = api.data['block']
    blockType = api.data['type']
    logger.info('blockType is ' + blockType)
    utils = api.get_utils()
    core = api.get_core()

    # Process specific block types

    # forwardKey blocks, add a new forward secrecy key for a peer
    if blockType == 'forwardKey':
        if api.data['validSig'] == True:
            _processForwardKey(api, myBlock)
    # socket blocks
    elif blockType == 'con':
        if api.data['validSig'] == True and myBlock.decrypted: # we check if it is decrypted as a way of seeing if it was for us
            myBlock.bcontent = utils.bytesToStr(myBlock.bcontent)
            if utils.validateID('%s.onion' % (myBlock.bcontent,)):
                logger.info('Detected socket advertised to us...')
                core.keyStore.put('con', (myBlock.content, myBlock.signer))

def on_init(api, data = None):

    pluginapi = api

    return
