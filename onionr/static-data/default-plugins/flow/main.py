'''
    Onionr - Private P2P Communication

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
import threading, time, locale, sys, os
from onionrblockapi import Block
import logger, config, onionrblocks
from onionrutils import escapeansi, epoch, bytesconverter
locale.setlocale(locale.LC_ALL, '')
from coredb import blockmetadb
from utils import identifyhome, reconstructhash
import deadsimplekv as simplekv
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import flowapi # import after path insert
flask_blueprint = flowapi.flask_blueprint
security_whitelist = ['staticfiles.boardContent', 'staticfiles.board']

plugin_name = 'flow'
PLUGIN_VERSION = '0.0.1'

class OnionrFlow:
    def __init__(self):
        self.alreadyOutputed = []
        self.flowRunning = False
        self.channel = ""
        return

    def start(self):
        logger.warn("Please note: everything said here is public, even if a random channel name is used.", terminal=True)
        message = ""
        self.flowRunning = True
        try:
            self.channel = logger.readline("Enter a channel name or none for default:").strip()
        except (KeyboardInterrupt, EOFError) as e:
            self.flowRunning = False
        newThread = threading.Thread(target=self.showOutput, daemon=True)
        newThread.start()
        while self.flowRunning:
            if self.channel == "":
                self.channel = "global"
            try:
                message = logger.readline('\nInsert message into flow:').strip().replace('\n', '\\n').replace('\r', '\\r')
            except EOFError:
                pass
            except KeyboardInterrupt:
                self.flowRunning = False
            else:
                if message == "q":
                    self.flowRunning = False
                expireTime = epoch.get_epoch() + 43200
                if len(message) > 0:
                    logger.info('Inserting message as block...', terminal=True)
                    onionrblocks.insert(message, header='brd', expire=expireTime, meta={'ch': self.channel})

        logger.info("Flow is exiting, goodbye", terminal=True)
        return

    def showOutput(self):
        while type(self.channel) is type(None) and self.flowRunning:
            time.sleep(1)
        try:
            while self.flowRunning:
                for block in blockmetadb.get_blocks_by_type('brd'):
                    if block in self.alreadyOutputed:
                        continue
                    block = Block(block)
                    b_hash = bytesconverter.bytes_to_str(block.getHash())
                    if block.getMetadata('ch') != self.channel:
                        continue
                    if not self.flowRunning:
                        break
                    logger.info('\n------------------------', prompt = False, terminal=True)
                    content = block.getContent()
                    # Escape new lines, remove trailing whitespace, and escape ansi sequences
                    content = escapeansi.escape_ANSI(content.replace('\n', '\\n').replace('\r', '\\r').strip())
                    logger.info(block.getDate().strftime("%m/%d %H:%M") + ' - ' + logger.colors.reset + content, prompt = False, terminal=True)
                    self.alreadyOutputed.append(b_hash)
                time.sleep(5)
        except KeyboardInterrupt:
            self.flowRunning = False

def on_flow_cmd(api, data=None):
    OnionrFlow().start()

def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''
    return

def on_processblocks(api, data=None):
    metadata = data['block'].bmetadata # Get the block metadata
    if data['type'] != 'brd':
        return

    b_hash = reconstructhash.deconstruct_hash(data['block'].hash) # Get the 0-truncated block hash
    board_cache = simplekv.DeadSimpleKV(identifyhome.identify_home() + '/board-index.cache.json', flush_on_exit=False) # get the board index cache
    board_cache.refresh()
    # Validate the channel name is sane for caching
    try:
        ch = metadata['ch']
    except KeyError:
        ch = 'global'
    ch_len = len(ch)
    if ch_len == 0:
        ch = 'global'
    elif ch_len > 12:
        return
    
    existing_posts = board_cache.get(ch)
    if existing_posts is None:
        existing_posts = []
    existing_posts.append(data['block'].hash)
    board_cache.put(ch, existing_posts)
    board_cache.flush()
