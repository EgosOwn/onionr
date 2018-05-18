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
import logger, config, core
import os, sqlite3, threading
from onionrblockapi import Block

plugin_name = 'gui'

def send():
    global message
    block = Block()
    block.setType('txt')
    block.setContent(message)
    logger.debug('Sent message in block %s.' % block.save(sign = True))


def sendMessage():
    global sendEntry

    global message
    message = sendEntry.get()

    t = threading.Thread(target = send)
    t.start()

    sendEntry.delete(0, len(message))

def update():
    global listedBlocks, listbox, runningCheckDelayCount, runningCheckDelay, root, daemonStatus

    for i in Block.getBlocks(type = 'txt'):
        if i.getContent().strip() == '' or i.getHash() in listedBlocks:
            continue
        listbox.insert(99999, str(i.getContent()))
        listedBlocks.append(i.getHash())
        listbox.see(99999)

    runningCheckDelayCount += 1

    if runningCheckDelayCount == runningCheckDelay:
        resp = pluginapi.daemon.local_command('ping')
        if resp == 'pong':
            daemonStatus.config(text = "Onionr Daemon Status: Running")
        else:
            daemonStatus.config(text = "Onionr Daemon Status: Not Running")
        runningCheckDelayCount = 0
    root.after(10000, update)


def reallyOpenGUI():
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
    logger.debug('Onionr Hostname: %s' % hostname)
    idText = hostname

    idEntry = tkinter.Entry(nodeInfo)
    tkinter.Label(nodeInfo, text = "Node Address: ").pack(side=tkinter.LEFT)
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

def openGUI():
    t = threading.Thread(target = reallyOpenGUI)
    t.daemon = False
    t.start()

def on_init(api, data = None):
    global pluginapi
    pluginapi = api

    api.commands.register(['gui', 'launch-gui', 'open-gui'], openGUI)
    api.commands.register_help('gui', 'Opens a graphical interface for Onionr')

    return
