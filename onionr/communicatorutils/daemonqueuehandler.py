'''
    Onionr - P2P Anonymous Storage Network

    Handle daemon queue commands in the communicator
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
import logger
import onionrevents as events
from onionrutils import localcommand
from coredb import daemonqueue
import filepaths
from . import restarttor
def handle_daemon_commands(comm_inst):
    cmd = daemonqueue.daemon_queue()
    response = ''
    if cmd is not False:
        events.event('daemon_command', data = {'cmd' : cmd})
        if cmd[0] == 'shutdown':
            comm_inst.shutdown = True
        elif cmd[0] == 'remove_from_insert_list':
            comm_inst.generating_blocks.remove(cmd[1])
        elif cmd[0] == 'announceNode':
            if len(comm_inst.onlinePeers) > 0:
                comm_inst.announce(cmd[1])
            else:
                logger.debug("No nodes connected. Will not introduce node.")
        elif cmd[0] == 'runCheck': # deprecated
            logger.debug('Status check; looks good.')
            open(filepaths.run_check_file + '.runcheck', 'w+').close()
        elif cmd[0] == 'connectedPeers':
            response = '\n'.join(list(comm_inst.onlinePeers)).strip()
            if response == '':
                response = 'none'
        elif cmd[0] == 'localCommand':
            response = localcommand.local_command(cmd[1])
        elif cmd[0] == 'clearOffline':
            comm_inst.offlinePeers = []
        elif cmd[0] == 'restartTor':
            restarttor.restart(comm_inst)
            comm_inst.offlinePeers = []
        elif cmd[0] == 'pex':
            for i in comm_inst.timers:
                if i.timerFunction.__name__ == 'lookupAdders':
                    i.count = (i.frequency - 1)
        elif cmd[0] == 'uploadBlock':
            comm_inst.blocksToUpload.append(cmd[1])

        if cmd[0] not in ('', None):
            if response != '':
                localcommand.local_command('queueResponseAdd/' + cmd[4], post=True, postData={'data': response})
        response = ''

    comm_inst.decrementThreadCount('handle_daemon_commands')
