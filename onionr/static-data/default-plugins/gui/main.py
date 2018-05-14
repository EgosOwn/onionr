#!/usr/bin/python
'''
    Onionr - P2P Microblogging Platform & Social network
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
import logger, config
import os, sqlite3, core

plugin_name = 'gui'

def sendMessage():
    global sendEntry

    messageToAdd = '-txt-' + sendEntry.get()
    #addedHash = pluginapi.get_core().setData(messageToAdd)
    #pluginapi.get_core().addToBlockDB(addedHash, selfInsert=True)
    #pluginapi.get_core().setBlockType(addedHash, 'txt')
    pluginapi.get_core().insertBlock(messageToAdd, header='txt', sign=True)
    sendEntry.delete(0, END)

def update():
    global listedBlocks, listbox, runningCheckDelayCount, runningCheckDelay, root, daemonStatus

    # TO DO: migrate to new header format
    for i in pluginapi.get_core().getBlocksByType('txt'):
        if i.strip() == '' or i in listedBlocks:
            continue
        blockFile = open('./data/blocks/' + i + '.dat')
        listbox.insert(END, str(blockFile.read().replace('-txt-', '')))
        blockFile.close()
        listedBlocks.append(i)
        listbox.see(END)
    blocksList = os.listdir('./data/blocks/') # dir is your directory path
    number_blocks = len(blocksList)
    runningCheckDelayCount += 1

    if runningCheckDelayCount == runningCheckDelay:
        resp = pluginapi.get_core()._utils.localCommand('ping')
        if resp == 'pong':
            daemonStatus.config(text="Onionr Daemon Status: Running")
        else:
            daemonStatus.config(text="Onionr Daemon Status: Not Running")
        runningCheckDelayCount = 0
    root.after(10000, update)


def openGUI():
    import tkinter
    global root, runningCheckDelay, runningCheckDelayCount, scrollbar, listedBlocks, nodeInfo, keyInfo, idText, idEntry, pubKeyEntry, listbox, daemonStatus, sendEntry

    root = tkinter.Tk()

    root.title("Onionr GUI")

    runningCheckDelay = 5
    runningCheckDelayCount = 4

    scrollbar = tkinter.Scrollbar(root)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    listedBlocks = []

    nodeInfo = tkinter.Frame(root)
    keyInfo = tkinter.Frame(root)

    hostname = pluginapi.get_onionr().get_hostname()
    logger.debug('hostname: %s' % hostname)
    idText = hostname

    idEntry = tkinter.Entry(nodeInfo)
    tkinter.Label(nodeInfo, text="Node Address: ").pack(side=tkinter.LEFT)
    idEntry.pack()
    idEntry.insert(0, idText.strip())
    idEntry.configure(state="readonly")

    nodeInfo.pack()

    pubKeyEntry = tkinter.Entry(keyInfo)

    tkinter.Label(keyInfo, text="Public key: ").pack(side=tkinter.LEFT)

    pubKeyEntry.pack()
    pubKeyEntry.insert(0, pluginapi.get_core()._crypto.pubKey)
    pubKeyEntry.configure(state="readonly")

    keyInfo.pack()

    sendEntry = tkinter.Entry(root)
    sendBtn = tkinter.Button(root, text='Send Message', command=sendMessage)
    sendEntry.pack(side=tkinter.TOP, pady=5)
    sendBtn.pack(side=tkinter.TOP)

    listbox = tkinter.Listbox(root, yscrollcommand=tkinter.Scrollbar.set, height=15)

    listbox.pack(fill=tkinter.BOTH, pady=25)

    daemonStatus = tkinter.Label(root, text="Onionr Daemon Status: unknown")
    daemonStatus.pack()

    scrollbar.config(command=tkinter.Listbox.yview)
    root.after(2000, update)
    root.mainloop()

def on_init(api, data = None):
    global pluginapi
    pluginapi = api

    api.commands.register(['gui', 'launch-gui', 'open-gui'], openGUI)
    api.commands.register_help('gui', 'Opens a graphical interface for Onionr')

    return
