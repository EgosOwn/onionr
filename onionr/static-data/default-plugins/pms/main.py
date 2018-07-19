'''
    Onionr - P2P Microblogging Platform & Social network

    This default plugin handles private messages in an email like fashion
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
import logger, config, threading, time, readline, datetime
from onionrblockapi import Block
import onionrexceptions

plugin_name = 'pms'
PLUGIN_VERSION = '0.0.1'

def draw_border(text):
    #https://stackoverflow.com/a/20757491
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    res = ['┌' + '─' * width + '┐']
    for s in lines:
        res.append('│' + (s + ' ' * width)[:width] + '│')
    res.append('└' + '─' * width + '┘')
    return '\n'.join(res)


class MailStrings:
    def __init__(self, mailInstance):
        self.mailInstance = mailInstance

        self.programTag = 'OnionrMail v%s' % (PLUGIN_VERSION)
        choices = ['view inbox', 'view sentbox', 'send message', 'help', 'quit']
        self.mainMenuChoices = choices
        self.mainMenu = '''\n
-----------------
1. %s
2. %s
3. %s
4. %s
5. %s''' % (choices[0], choices[1], choices[2], choices[3], choices[4])

class OnionrMail:
    def __init__(self, pluginapi):
        self.myCore = pluginapi.get_core()
        #self.dataFolder = pluginapi.get_data_folder()
        self.strings = MailStrings(self)

        return
    
    def inbox(self):
        blockCount = 0
        pmBlockMap = {}
        pmBlocks = {}
        logger.info('Decrypting messages...')
        choice = ''

        # this could use a lot of memory if someone has recieved a lot of messages
        for blockHash in self.myCore.getBlocksByType('pm'):
            pmBlocks[blockHash] = Block(blockHash, core=self.myCore)
            pmBlocks[blockHash].decrypt()

        while choice not in ('-q', 'q', 'quit'):
            blockCount = 0
            for blockHash in pmBlocks:
                if not pmBlocks[blockHash].decrypted:
                    continue
                blockCount += 1
                pmBlockMap[blockCount] = blockHash
                blockDate = pmBlocks[blockHash].getDate().strftime("%m/%d %H:%M")
                print('%s. %s: %s' % (blockCount, blockDate, blockHash))

            try:
                choice = logger.readline('Enter a block number, -r to refresh, or -q to stop: ').strip().lower()
            except (EOFError, KeyboardInterrupt):
                choice = '-q'

            if choice in ('-q', 'q', 'quit'):
                continue

            if choice in ('-r', 'r', 'refresh'):
                # dirty hack
                self.inbox()
                return

            try:
                choice = int(choice)
            except ValueError:
                pass
            else:
                try:
                    pmBlockMap[choice]
                    readBlock = pmBlocks[pmBlockMap[choice]]
                except KeyError:
                    pass
                else:
                    readBlock.verifySig()
                    print('Message recieved from', readBlock.signer)
                    print('Valid signature:', readBlock.validSig)
                    if not readBlock.validSig:
                        logger.warn('This message has an INVALID signature. Anyone could have sent this message.')
                        logger.readline('Press enter to continue to message.')

                    print(draw_border(self.myCore._utils.escapeAnsi(readBlock.bcontent.decode().strip())))

        return
    
    def draftMessage(self):
        message = ''
        newLine = ''
        recip = ''
        entering = True

        while entering:
            try:
                recip = logger.readline('Enter peer address, or q to stop:').strip()
                if recip in ('-q', 'q'):
                    raise EOFError
                if not self.myCore._utils.validatePubKey(recip):
                    raise onionrexceptions.InvalidPubkey('Must be a valid ed25519 base32 encoded public key')
            except onionrexceptions.InvalidPubkey:
                logger.warn('Invalid public key')
            except (KeyboardInterrupt, EOFError):
                entering = False
            else:
                break
        else:
            # if -q or ctrl-c/d, exit function here, otherwise we successfully got the public key
            return

        print('Enter your message, stop by entering -q on a new line.')
        while newLine != '-q':
            try:
                newLine = input()
            except (KeyboardInterrupt, EOFError):
                pass
            if newLine == '-q':
                continue
            newLine += '\n'
            message += newLine

        print('Inserting encrypted message as Onionr block....')

        self.myCore.insertBlock(message, header='pm', encryptType='asym', asymPeer=recip, sign=True)

    def menu(self):
        choice = ''
        while True:

            print(self.strings.programTag + '\n\nOur ID: ' + self.myCore._crypto.pubKey + self.strings.mainMenu.title()) # print out main menu

            try:
                choice = logger.readline('Enter 1-%s:\n' % (len(self.strings.mainMenuChoices))).lower().strip()
            except (KeyboardInterrupt, EOFError):
                choice = '5'

            if choice in (self.strings.mainMenuChoices[0], '1'):
                self.inbox()
            elif choice in (self.strings.mainMenuChoices[1], '2'):
                logger.warn('not implemented yet')
            elif choice in (self.strings.mainMenuChoices[2], '3'):
                self.draftMessage()
            elif choice in (self.strings.mainMenuChoices[3], '4'):
                logger.warn('not implemented yet')
            elif choice in (self.strings.mainMenuChoices[4], '5'):
                logger.info('Goodbye.')
                break
            elif choice == '':
                pass
            else:
                logger.warn('Invalid choice.')
        return


def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    pluginapi = api
    mail = OnionrMail(pluginapi)
    api.commands.register(['mail'], mail.menu)
    api.commands.register_help('mail', 'Interact with OnionrMail')
    return