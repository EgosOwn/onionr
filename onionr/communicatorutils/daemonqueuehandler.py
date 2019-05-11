'''
    Onionr - P2P Microblogging Platform & Social network

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
def handle_daemon_commands(comm_inst):
    cmd = comm_inst._core.daemonQueue()
    response = ''
    if cmd is not False:
        events.event('daemon_command', onionr = None, data = {'cmd' : cmd})
        if cmd[0] == 'shutdown':
            comm_inst.shutdown = True
        elif cmd[0] == 'announceNode':
            if len(comm_inst.onlinePeers) > 0:
                comm_inst.announce(cmd[1])
            else:
                logger.debug("No nodes connected. Will not introduce node.")
        elif cmd[0] == 'runCheck': # deprecated
            logger.debug('Status check; looks good.')
            open(comm_inst._core.dataDir + '.runcheck', 'w+').close()
        elif cmd[0] == 'connectedPeers':
            response = '\n'.join(list(comm_inst.onlinePeers)).strip()
            if response == '':
                response = 'none'
        elif cmd[0] == 'localCommand':
            response = comm_inst._core._utils.localCommand(cmd[1])
        elif cmd[0] == 'pex':
            for i in comm_inst.timers:
                if i.timerFunction.__name__ == 'lookupAdders':
                    i.count = (i.frequency - 1)
        elif cmd[0] == 'uploadBlock':
            comm_inst.blocksToUpload.append(cmd[1])

        if cmd[0] not in ('', None):
            if response != '':
                comm_inst._core._utils.localCommand('queueResponseAdd/' + cmd[4], post=True, postData={'data': response})
        response = ''

    comm_inst.decrementThreadCount('daemonCommands')