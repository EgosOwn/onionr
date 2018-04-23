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
from tkinter import *
import os, sqlite3, core

def sendMessage():
    global sendEntry

    messageToAdd = '-txt-' + sendEntry.get()
    addedHash = pluginapi.get_core().setData(messageToAdd)
    pluginapi.get_core().addToBlockDB(addedHash, selfInsert=True)
    pluginapi.get_core().setBlockType(addedHash, 'txt')
    sendEntry.delete(0, END)

def update():
    global listedBlocks, listbox, runningCheckDelayCount, runningCheckDelay, root, daemonStatus


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
    global root, runningCheckDelay, runningCheckDelayCount, scrollbar, listedBlocks, nodeInfo, keyInfo, idText, idEntry, pubKeyEntry, listbox, daemonStatus, sendEntry

    root = Tk()

    root.title("Onionr GUI")

    runningCheckDelay = 5
    runningCheckDelayCount = 4

    scrollbar = Scrollbar(root)
    scrollbar.pack(side=RIGHT, fill=Y)

    listedBlocks = []

    nodeInfo = Frame(root)
    keyInfo = Frame(root)

    print(pluginapi.get_onionr().get_hostname())
    idText = pluginapi.get_onionr().get_hostname()

    idEntry = Entry(nodeInfo)
    Label(nodeInfo, text="Node Address: ").pack(side=LEFT)
    idEntry.pack()
    idEntry.insert(0, idText.strip())
    idEntry.configure(state="readonly")

    nodeInfo.pack()

    pubKeyEntry = Entry(keyInfo)

    Label(keyInfo, text="Public key: ").pack(side=LEFT)

    pubKeyEntry.pack()
    pubKeyEntry.insert(0, pluginapi.get_core()._crypto.pubKey)
    pubKeyEntry.configure(state="readonly")

    keyInfo.pack()

    sendEntry = Entry(root)
    sendBtn = Button(root, text='Send Message', command=sendMessage)
    sendEntry.pack(side=TOP, pady=5)
    sendBtn.pack(side=TOP)

    listbox = Listbox(root, yscrollcommand=scrollbar.set, height=15)

    listbox.pack(fill=BOTH, pady=25)

    daemonStatus = Label(root, text="Onionr Daemon Status: unknown")
    daemonStatus.pack()

    scrollbar.config(command=listbox.yview)
    root.after(2000, update)
    root.mainloop()

def on_init(api, data = None):
    global pluginapi
    pluginapi = api

    api.commands.register(['gui', 'launch-gui', 'open-gui'], openGUI)
    api.commands.register_help('gui', 'Opens a graphical interface for Onionr')

    return
