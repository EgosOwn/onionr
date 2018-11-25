'''
    Onionr - P2P Microblogging Platform & Social network

    This default plugin handles "flow" messages (global chatroom style communication)
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

# Imports some useful libraries
import logger, config, threading, time
from onionrblockapi import Block

plugin_name = 'flow'

class OnionrFlow:
    def __init__(self):
        self.myCore = pluginapi.get_core()
        self.alreadyOutputed = []
        self.flowRunning = False
        self.channel = None
        return

    def start(self):
        logger.warn("Please note: everything said here is public, even if a random channel name is used.")
        message = ""
        self.flowRunning = True
        newThread = threading.Thread(target=self.showOutput)
        newThread.start()
        try:
            self.channel = logger.readline("Enter a channel name or none for default:")
        except (KeyboardInterrupt, EOFError) as e:
            self.flowRunning = False
        while self.flowRunning:
            try:
                message = logger.readline('\nInsert message into flow:').strip().replace('\n', '\\n').replace('\r', '\\r')
            except EOFError:
                pass
            except KeyboardInterrupt:
                self.flowRunning = False
            else:
                if message == "q":
                    self.flowRunning = False
                expireTime = self.myCore._utils.getEpoch() + 43200
                if len(message) > 0:
                    insertBL = Block(content = message, type = 'txt', expire=expireTime, core = self.myCore)
                    insertBL.setMetadata('ch', self.channel)
                    insertBL.save()

        logger.info("Flow is exiting, goodbye")
        return

    def showOutput(self):
        while type(self.channel) is type(None) and self.flowRunning:
            time.sleep(1)
        try:
            while self.flowRunning:
                    for block in Block.getBlocks(type = 'txt', core = self.myCore):
                        if block.getMetadata('ch') != self.channel:
                            continue
                        if block.getHash() in self.alreadyOutputed:
                            continue
                        if not self.flowRunning:
                            break
                        logger.info('\n------------------------', prompt = False)
                        content = block.getContent()
                        # Escape new lines, remove trailing whitespace, and escape ansi sequences
                        content = self.myCore._utils.escapeAnsi(content.replace('\n', '\\n').replace('\r', '\\r').strip())
                        logger.info(block.getDate().strftime("%m/%d %H:%M") + ' - ' + logger.colors.reset + content, prompt = False)
                        self.alreadyOutputed.append(block.getHash())
                        time.sleep(5)
        except KeyboardInterrupt:
            self.flowRunning = False

def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    # Doing this makes it so that the other functions can access the api object
    # by simply referencing the variable `pluginapi`.
    global pluginapi
    pluginapi = api
    flow = OnionrFlow()
    api.commands.register('flow', flow.start)
    api.commands.register_help('flow', 'Open the flow messaging interface')
    return
