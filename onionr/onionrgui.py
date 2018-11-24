#!/usr/bin/env python3
from tkinter import *
import core
class OnionrGUI:
    def __init__(self):
        self.dataDir = "/programming/onionr/data/"
        self.root = Tk()
        self.root.geometry("450x250")
        self.core = core.Core()
        menubar = Menu(self.root)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=None)
        filemenu.add_command(label="Save", command=None)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        settingsmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settingsmenu)

        helpmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.root.config(menu=menubar)

        self.menuFrame = Frame(self.root)
        self.mainButton = Button(self.menuFrame, text="Main View")
        self.mainButton.grid(row=0, column=0, padx=0, pady=2, sticky=N+W)
        self.tabButton1 = Button(self.menuFrame, text="Mail")
        self.tabButton1.grid(row=0, column=1, padx=0, pady=2, sticky=N+W)
        self.tabButton2 = Button(self.menuFrame, text="Message Flow")
        self.tabButton2.grid(row=0, column=3, padx=0, pady=2, sticky=N+W)

        self.menuFrame.grid(row=0, column=0, padx=2, pady=0, sticky=N+W)


        self.idFrame = Frame(self.root)

        self.ourIDLabel = Label(self.idFrame, text="ID: ")
        self.ourIDLabel.grid(row=2, column=0, padx=1, pady=1, sticky=N+W)
        self.ourID = Entry(self.idFrame)
        self.ourID.insert(0, self.core._crypto.pubKey)
        self.ourID.grid(row=2, column=1, padx=1, pady=1, sticky=N+W)
        self.ourID.config(state='readonly')
        self.idFrame.grid(row=1, column=0, padx=2, pady=2, sticky=N+W)

        self.syncStatus = Label(self.root, text="Sync Status: 15/100")
        self.syncStatus.place(relx=1.0, rely=1.0, anchor=S+E)
        self.peerCount = Label(self.root, text="Connected Peers: 3")
        self.peerCount.place(relx=0.0, rely=1.0, anchor='sw')

        self.root.wm_title("Onionr")
        self.root.mainloop()
        return

OnionrGUI()