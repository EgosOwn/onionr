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

        w = Label(self.root, text="Onionr", width=10)
        w.config(font=("Sans-Serif", 22))
        w.pack()
        scrollbar = Scrollbar(self.root)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.listedBlocks = []

        idText = open('./data/hs/hostname', 'r').read()
        idLabel = Label(self.root, text="ID: " + idText)
        idLabel.pack(pady=5)

        self.listbox = Listbox(self.root, yscrollcommand=scrollbar.set)

        #listbox.insert(END, str(i))
        self.listbox.pack(fill=BOTH)

        scrollbar.config(command=self.listbox.yview)
        self.root.after(2000, self.update)
        self.root.mainloop() 

    def update(self):
        for i in self.myCore.getBlocksByType('txt'):
            if i.strip() == '' or i in self.listedBlocks:
                continue
            blockFile = open('./data/blocks/' + i + '.dat')
            self.listbox.insert(END, str(blockFile.read().replace('-txt-', '')))
            blockFile.close()
            self.listedBlocks.append(i)
        blocksList = os.listdir('./data/blocks/') # dir is your directory path
        number_blocks = len(blocksList)

        self.root.after(10000, self.update)
