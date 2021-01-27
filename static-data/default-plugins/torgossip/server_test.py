#!/usr/bin/env python

import socket
import os

#home = input("Enter Onionr data directory")
home = "/dev/shm/DATA24688"

def client(data):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(f'{home}/torgossip.sock')
        s.sendall(data)
        resp = s.recv(1024)
        print("\n", resp)

while True:
    print("1. ping")
    print('2. check block hash')
    print('3 list blocks')
    print("4. exit")
    inp = input()
    if inp == "1":
        client(b'1')
    elif inp == "3":
        client(b"3" + input("type: ").encode('utf8'))
    elif inp == "2":
        client(b'2' + os.urandom(32))
    elif inp == "3":
        client(b'3')
