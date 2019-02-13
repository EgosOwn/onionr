'''
    Onionr - P2P Anonymous Storage Network

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
import onionrexceptions, onionrusers
import locale, sys, os, json

locale.setlocale(locale.LC_ALL, '')

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import sentboxdb # import after path insert

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
        choices = ['view inbox', 'view sentbox', 'send message', 'toggle pseudonymity', 'quit']
        self.mainMenuChoices = choices
        self.mainMenu = '''-----------------
    1. %s
    2. %s
    3. %s
    4. %s
    5. %s''' % (choices[0], choices[1], choices[2], choices[3], choices[4])

class OnionrMail:
    def __init__(self, pluginapi):
        self.myCore = pluginapi.get_core()
        self.strings = MailStrings(self)

        self.sentboxTools = sentboxdb.SentBox(self.myCore)
        self.sentboxList = []
        self.sentMessages = {}
        self.doSigs = True
        return

    def inbox(self):
        blockCount = 0
        pmBlockMap = {}
        pmBlocks = {}
        logger.info('Decrypting messages...')
        choice = ''
        displayList = []
        subject = ''

        # this could use a lot of memory if someone has recieved a lot of messages
        for blockHash in self.myCore.getBlocksByType('pm'):
            pmBlocks[blockHash] = Block(blockHash, core=self.myCore)
            pmBlocks[blockHash].decrypt()
            blockCount = 0
        for blockHash in pmBlocks:
            if not pmBlocks[blockHash].decrypted:
                continue
            blockCount += 1
            pmBlockMap[blockCount] = blockHash

            block = pmBlocks[blockHash]
            senderKey = block.signer
            try:
                senderKey = senderKey.decode()
            except AttributeError:
                pass
            senderDisplay = onionrusers.OnionrUser(self.myCore, senderKey).getName()
            if senderDisplay == 'anonymous':
                senderDisplay = senderKey

            blockDate = pmBlocks[blockHash].getDate().strftime("%m/%d %H:%M")
            try:
                subject = pmBlocks[blockHash].bmetadata['subject']
            except KeyError:
                subject = ''
            
            displayList.append('%s. %s - %s - <%s>: %s' % (blockCount, blockDate, senderDisplay[:12], subject[:10], blockHash))
        while choice not in ('-q', 'q', 'quit'):
            for i in displayList:
                logger.info(i)
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
                    cancel = ''
                    readBlock.verifySig()
                    senderDisplay = self.myCore._utils.bytesToStr(readBlock.signer)
                    if len(senderDisplay.strip()) == 0:
                        senderDisplay = 'Anonymous'
                    logger.info('Message received from %s' % (senderDisplay,))
                    logger.info('Valid signature: %s' % readBlock.validSig)

                    if not readBlock.validSig:
                        logger.warn('This message has an INVALID/NO signature. ANYONE could have sent this message.')
                        cancel = logger.readline('Press enter to continue to message, or -q to not open the message (recommended).')
                    if cancel != '-q':
                        try:
                            print(draw_border(self.myCore._utils.escapeAnsi(readBlock.bcontent.decode().strip())))
                        except ValueError:
                            logger.warn('Error presenting message. This is usually due to a malformed or blank message.')
                            pass
                        reply = logger.readline("Press enter to continue, or enter %s to reply" % ("-r",))
                        print('')
                        if reply == "-r":
                            self.draft_message(self.myCore._utils.bytesToStr(readBlock.signer,))
        return

    def sentbox(self):
        '''
            Display sent mail messages
        '''
        entering = True
        while entering:
            self.get_sent_list()
            logger.info('Enter a block number or -q to return')
            try:
                choice = input('>')
            except (EOFError, KeyboardInterrupt) as e:
                entering = False
            else:
                try:
                    choice = int(choice) - 1
                except ValueError:
                    pass
                else:
                    try:
                        self.sentboxList[int(choice)]
                    except (IndexError, ValueError) as e:
                        logger.warn('Invalid block.')
                    else:
                        logger.info('Sent to: ' + self.sentMessages[self.sentboxList[int(choice)]][1])
                        # Print ansi escaped sent message
                        logger.info(self.myCore._utils.escapeAnsi(self.sentMessages[self.sentboxList[int(choice)]][0]))
                        input('Press enter to continue...')
                finally:
                    if choice == '-q':
                        entering = False

        return

    def get_sent_list(self, display=True):
        count = 1
        self.sentboxList = []
        self.sentMessages = {}
        for i in self.sentboxTools.listSent():
            self.sentboxList.append(i['hash'])
            self.sentMessages[i['hash']] = (self.myCore._utils.bytesToStr(i['message']), i['peer'], i['subject'])
            if display:
                logger.info('%s. %s - %s - (%s) - %s' % (count, i['hash'], i['peer'][:12], i['subject'], i['date']))
            count += 1
        return json.dumps(self.sentMessages)

    def draft_message(self, recip=''):
        message = ''
        newLine = ''
        subject = ''
        entering = False
        if len(recip) == 0:
            entering = True
            while entering:
                try:
                    recip = logger.readline('Enter peer address, or -q to stop:').strip()
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
        try:
            subject = logger.readline('Message subject: ')
        except (KeyboardInterrupt, EOFError):
            pass
        
        cancelEnter = False
        logger.info('Enter your message, stop by entering -q on a new line. -c to cancel')
        while newLine != '-q':
            try:
                newLine = input()
            except (KeyboardInterrupt, EOFError):
                cancelEnter = True
            if newLine == '-c':
                cancelEnter = True
                break
            if newLine == '-q':
                continue
            newLine += '\n'
            message += newLine

        if not cancelEnter:
            logger.info('Inserting encrypted message as Onionr block....')

            blockID = self.myCore.insertBlock(message, header='pm', encryptType='asym', asymPeer=recip, sign=self.doSigs, meta={'subject': subject})
    
    def toggle_signing(self):
        self.doSigs = not self.doSigs
    
    def menu(self):
        choice = ''
        while True:
            sigMsg = 'Message Signing: %s'

            logger.info(self.strings.programTag + '\n\nUser ID: ' + self.myCore._crypto.pubKey)
            if self.doSigs:
                sigMsg = sigMsg % ('enabled',)
            else:
                sigMsg = sigMsg % ('disabled (Your messages cannot be trusted)',)
            if self.doSigs:
                logger.info(sigMsg)
            else:
                logger.warn(sigMsg)
            logger.info(self.strings.mainMenu.title()) # print out main menu
            try:
                choice = logger.readline('Enter 1-%s:\n' % (len(self.strings.mainMenuChoices))).lower().strip()
            except (KeyboardInterrupt, EOFError):
                choice = '5'

            if choice in (self.strings.mainMenuChoices[0], '1'):
                self.inbox()
            elif choice in (self.strings.mainMenuChoices[1], '2'):
                self.sentbox()
            elif choice in (self.strings.mainMenuChoices[2], '3'):
                self.draft_message()
            elif choice in (self.strings.mainMenuChoices[3], '4'):
                self.toggle_signing()
            elif choice in (self.strings.mainMenuChoices[4], '5'):
                logger.info('Goodbye.')
                break
            elif choice == '':
                pass
            else:
                logger.warn('Invalid choice.')
        return

def on_insertblock(api, data={}):
    sentboxTools = sentboxdb.SentBox(api.get_core())
    meta = json.loads(data['meta'])
    sentboxTools.addToSent(data['hash'], data['peer'], data['content'], meta['subject'])

def on_pluginrequest(api, data=None):
    resp = ''
    subject = ''
    recip = ''
    message = ''
    postData = {}
    blockID = ''
    sentboxTools = sentboxdb.SentBox(api.get_core())
    if data['name'] == 'mail':
        path = data['path']
        cmd = path.split('/')[1]
        if cmd == 'sentbox':
            resp = OnionrMail(api).get_sent_list(display=False)
    if resp != '':
        api.get_onionr().clientAPIInst.pluginResponses[data['pluginResponse']] = resp

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
