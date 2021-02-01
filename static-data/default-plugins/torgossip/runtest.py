import socket
import os
from threading import local

from utils import identifyhome
from onionrblocks import blockcreator
from blockio import subprocgenerate
from onionrutils import localcommand
import blockio

def torgossip_runtest(test_manager):


    s_file = identifyhome.identify_home() + "/torgossip.sock"
    bl_test = blockcreator.create_anonvdf_block(b"test", "txt", 10)

    #test_manager._too_many.get_by_string("PassToSafeDB").queue_then_store(b"test", "txt", 10)
    bl = subprocgenerate.vdf_block(b"test", "txt", 100)
    blockio.store_block(bl, test_manager._too_many.get_by_string("SafeDB"))

    tsts = b''
    for i in range(3):
        bl = subprocgenerate.vdf_block(b"test" + os.urandom(3), "tst", 100)
        tsts += bl.id
        blockio.store_block(bl, test_manager._too_many.get_by_string("SafeDB"))

    bl_new = blockcreator.create_anonvdf_block(b"test5", "txt", 10)


    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(s_file)
        s.sendall(b'1')
        resp = s.recv(5)
        assert resp == b"PONG"

        s.sendall(b'3txx')
        assert s.recv(64) == b"0"

        s.sendall(b'3txt')
        assert bl.id in s.recv(10000)

        # test getting a block that doesn't exist
        s.sendall(b'5' + os.urandom(64))
        assert s.recv(64) == b"0"

        # test getting a block that does exist
        s.sendall(b'5' + bl.id)
        assert s.recv(64) == bl.get_packed()

        # test putting block
        s.sendall(b'6' + bl_new.id + bl_new.get_packed())
        assert s.recv(2) == b"1"

        # test block was uploaded by getting it
        s.sendall(b'5' + bl_new.id)
        assert s.recv(64) == bl_new.get_packed()

        # test block was uploaded by getting it
        s.sendall(b'7')
        assert s.recv(64) == b"BYE"

        s.sendall(b'41tst')
        assert s.recv(1000) == tsts[64:]

        s.sendall(b'42tst')
        assert s.recv(1000) == tsts[64*2:]

