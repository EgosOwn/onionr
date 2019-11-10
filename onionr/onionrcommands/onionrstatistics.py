'''
    Onionr - Private P2P Communication

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
import logger
from onionrblocks import onionrblockapi
from onionrblocks import onionrblacklist
from onionrutils import checkcommunicator, mnemonickeys
from utils import sizeutils, gethostname, getconsolewidth, identifyhome
from coredb import blockmetadb, daemonqueue, keydb
import onionrcrypto, config
from etc import onionrvalues
def show_stats():
    try:
        # define stats messages here
        totalBlocks = len(blockmetadb.get_block_list())
        home = identifyhome.identify_home()
        signedBlocks = len(onionrblockapi.Block.getBlocks(signed = True))
        totalBanned = len(onionrblacklist.OnionrBlackList().getList())

        messages = {
            # info about local client
            'Onionr Daemon Status' : ((logger.colors.fg.green + 'Online') if checkcommunicator.is_communicator_running(timeout = 9) else logger.colors.fg.red + 'Offline'),

            # file and folder size stats
            'div1' : True, # this creates a solid line across the screen, a div
            'Total Block Size' : sizeutils.human_size(sizeutils.size(home + 'blocks/')),
            'Total Plugin Size' : sizeutils.human_size(sizeutils.size(home + 'plugins/')),
            'Log File Size' : sizeutils.human_size(sizeutils.size(home + 'output.log')),

            # count stats
            'div2' : True,
            'Known Peers (nodes)' : str(max(len(keydb.listkeys.list_adders()) - 1, 0)),
            'Enabled Plugins' : str(len(config.get('plugins.enabled', list()))) + ' / ' + str(len(os.listdir(home + 'plugins/'))),
            'Stored Blocks' : str(totalBlocks),
            'Deleted Blocks' : str(totalBanned),
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
        width = getconsolewidth.get_console_width()
        for key, val in messages.items():
            if not (type(val) is bool and val is True):
                maxlength = max(len(key), maxlength)
        prewidth = maxlength + len(' | ')
        groupsize = width - prewidth - len('[+] ')

        # generate stats table
        logger.info(colors['title'] + 'Onionr v%s Statistics' % onionrvalues.ONIONR_VERSION + colors['reset'], terminal=True)
        logger.info(colors['border'] + '-' * (maxlength + 1) + '+' + colors['reset'], terminal=True)
        for key, val in messages.items():
            if not (type(val) is bool and val is True):
                val = [str(val)[i:i + groupsize] for i in range(0, len(str(val)), groupsize)]

                logger.info(colors['key'] + str(key).rjust(maxlength) + colors['reset'] + colors['border'] + ' | ' + colors['reset'] + colors['val'] + str(val.pop(0)) + colors['reset'], terminal=True)

                for value in val:
                    logger.info(' ' * maxlength + colors['border'] + ' | ' + colors['reset'] + colors['val'] + str(value) + colors['reset'], terminal=True)
            else:
                logger.info(colors['border'] + '-' * (maxlength + 1) + '+' + colors['reset'], terminal=True)
        logger.info(colors['border'] + '-' * (maxlength + 1) + '+' + colors['reset'], terminal=True)
    except Exception as e:
        logger.error('Failed to generate statistics table. ' + str(e), error = e, timestamp = False, terminal=True)

def show_details():
    details = {
        'Node Address' : gethostname.get_hostname(),
        'Public Key' : onionrcrypto.pub_key.replace('=', ''),
        'Human-readable Public Key' : mnemonickeys.get_human_readable_ID()
    }

    for detail in details:
        logger.info('%s%s: \n%s%s\n' % (logger.colors.fg.lightgreen, detail, logger.colors.fg.green, details[detail]), terminal = True)

show_details.onionr_help = "Shows relevant information for your Onionr install: node address,  and active public key."
show_stats.onionr_help = "Shows statistics for your Onionr node. Slow if Onionr is not running"
