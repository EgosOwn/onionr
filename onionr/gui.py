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
from tkinter import *
import os, sqlite3, core
class OnionrGUI:
    def __init__(self, myCore):
        self.root = Tk()

        self.myCore = myCore # onionr core
        self.root.title("PyOnionr")

        self.runningCheckDelay = 5
        self.runningCheckDelayCount = 4

        scrollbar = Scrollbar(self.root)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.listedBlocks = []

        self.nodeInfo = Frame(self.root)
        self.keyInfo = Frame(self.root)

        idText = open('./data/hs/hostname', 'r').read()
        #idLabel = Label(self.info, text="Node Address: " + idText)
        #idLabel.pack(pady=5)

        idEntry = Entry(self.nodeInfo)
        Label(self.nodeInfo, text="Node Address: ").pack(side=LEFT)
        idEntry.pack()
        idEntry.insert(0, idText.strip())
        idEntry.configure(state="readonly")

        self.nodeInfo.pack()

        pubKeyEntry = Entry(self.keyInfo)

        Label(self.keyInfo, text="Public key: ").pack(side=LEFT)

        pubKeyEntry.pack()
        pubKeyEntry.insert(0, self.myCore._crypto.pubKey)
        pubKeyEntry.configure(state="readonly")

        self.keyInfo.pack()

        self.sendEntry = Entry(self.root)
        sendBtn = Button(self.root, text='Send Message', command=self.sendMessage)
        self.sendEntry.pack(side=TOP, pady=5)
        sendBtn.pack(side=TOP)

        self.listbox = Listbox(self.root, yscrollcommand=scrollbar.set, height=15)

        #listbox.insert(END, str(i))
        self.listbox.pack(fill=BOTH, pady=25)

        self.daemonStatus = Label(self.root, text="Onionr Daemon Status: unknown")
        self.daemonStatus.pack()

        scrollbar.config(command=self.listbox.yview)
        self.root.after(2000, self.update)
        self.root.mainloop() 

    def sendMessage(self):
        messageToAdd = '-txt-' + self.sendEntry.get()
        addedHash = self.myCore.setData(messageToAdd)
        self.myCore.addToBlockDB(addedHash, selfInsert=True)
        self.myCore.setBlockType(addedHash, 'txt')
        self.sendEntry.delete(0, END)

    def update(self):
        for i in self.myCore.getBlocksByType('txt'):
            if i.strip() == '' or i in self.listedBlocks:
                continue
            blockFile = open('./data/blocks/' + i + '.dat')
            self.listbox.insert(END, str(blockFile.read().replace('-txt-', '')))
            blockFile.close()
            self.listedBlocks.append(i)
            self.listbox.see(END)
        blocksList = os.listdir('./data/blocks/') # dir is your directory path
        number_blocks = len(blocksList)
        self.runningCheckDelayCount += 1

        if self.runningCheckDelayCount == self.runningCheckDelay:
            if self.myCore._utils.localCommand('ping') == 'pong':
                self.daemonStatus.config(text="Onionr Daemon Status: Running")
            else:
                self.daemonStatus.config(text="Onionr Daemon Status: Not Running")
            self.runningCheckDelayCount = 0
        self.root.after(10000, self.update)
