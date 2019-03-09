'''
    Onionr - P2P Anonymous Storage Network

    This module defines commands to show stats/details about the local node
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
import os, uuid, time
import logger, onionrutils
from onionrblockapi import Block
import onionr

def show_stats(o_inst):
    try:
        # define stats messages here
        totalBlocks = len(o_inst.onionrCore.getBlockList())
        signedBlocks = len(Block.getBlocks(signed = True))
        messages = {
            # info about local client
            'Onionr Daemon Status' : ((logger.colors.fg.green + 'Online') if o_inst.onionrUtils.isCommunicatorRunning(timeout = 9) else logger.colors.fg.red + 'Offline'),

            # file and folder size stats
            'div1' : True, # this creates a solid line across the screen, a div
            'Total Block Size' : onionrutils.humanSize(onionrutils.size(o_inst.dataDir + 'blocks/')),
            'Total Plugin Size' : onionrutils.humanSize(onionrutils.size(o_inst.dataDir + 'plugins/')),
            'Log File Size' : onionrutils.humanSize(onionrutils.size(o_inst.dataDir + 'output.log')),

            # count stats
            'div2' : True,
            'Known Peers' : str(len(o_inst.onionrCore.listPeers()) - 1),
            'Enabled Plugins' : str(len(o_inst.onionrCore.config.get('plugins.enabled', list()))) + ' / ' + str(len(os.listdir(o_inst.dataDir + 'plugins/'))),
            'Stored Blocks' : str(totalBlocks),
            'Percent Blocks Signed' : str(round(100 * signedBlocks / max(totalBlocks, 1), 2)) + '%'
        }

        # color configuration
        colors = {
            'title' : logger.colors.bold,
            'key' : logger.colors.fg.lightgreen,
            'val' : logger.colors.fg.green,
            'border' : logger.colors.fg.lightblue,

            'reset' : logger.colors.reset
        }

        # pre-processing
        maxlength = 0
        width = o_inst.getConsoleWidth()
        for key, val in messages.items():
            if not (type(val) is bool and val is True):
                maxlength = max(len(key), maxlength)
        prewidth = maxlength + len(' | ')
        groupsize = width - prewidth - len('[+] ')

        # generate stats table
        logger.info(colors['title'] + 'Onionr v%s Statistics' % onionr.ONIONR_VERSION + colors['reset'])
        logger.info(colors['border'] + '-' * (maxlength + 1) + '+' + colors['reset'])
        for key, val in messages.items():
            if not (type(val) is bool and val is True):
                val = [str(val)[i:i + groupsize] for i in range(0, len(str(val)), groupsize)]

                logger.info(colors['key'] + str(key).rjust(maxlength) + colors['reset'] + colors['border'] + ' | ' + colors['reset'] + colors['val'] + str(val.pop(0)) + colors['reset'])

                for value in val:
                    logger.info(' ' * maxlength + colors['border'] + ' | ' + colors['reset'] + colors['val'] + str(value) + colors['reset'])
            else:
                logger.info(colors['border'] + '-' * (maxlength + 1) + '+' + colors['reset'])
        logger.info(colors['border'] + '-' * (maxlength + 1) + '+' + colors['reset'])
    except Exception as e:
        logger.error('Failed to generate statistics table.', error = e, timestamp = False)

def show_details(o_inst):
    details = {
        'Node Address' : o_inst.get_hostname(),
        'Web Password' : o_inst.getWebPassword(),
        'Public Key' : o_inst.onionrCore._crypto.pubKey,
        'Human-readable Public Key' : o_inst.onionrCore._utils.getHumanReadableID()
    }

    for detail in details:
        logger.info('%s%s: \n%s%s\n' % (logger.colors.fg.lightgreen, detail, logger.colors.fg.green, details[detail]), sensitive = True)

def show_peers(o_inst):
    randID = str(uuid.uuid4())
    o_inst.onionrCore.daemonQueueAdd('connectedPeers', responseID=randID)
    while True:
        try:
            time.sleep(3)
            peers = o_inst.onionrCore.daemonQueueGetResponse(randID)
        except KeyboardInterrupt:
            break
        if not type(peers) is None:
            if peers not in ('', 'failure', None):
                if peers != False:
                    print(peers)
                else:
                    print('Daemon probably not running. Unable to list connected peers.')
                break