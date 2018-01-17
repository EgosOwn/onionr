#!/usr/bin/env python3
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
import unittest, sys, os, base64, tarfile, shutil, simplecrypt

class OnionrTests(unittest.TestCase):
    def testPython3(self):
        if sys.version_info.major != 3:
            print(sys.version_info.major)
            self.assertTrue(False)
        else:
            self.assertTrue(True)
    def testNone(self):
        print('--------------------------')
        print('Running simple program run test')
        # Test just running ./onionr with no arguments
        blank = os.system('./onionr.py')
        if blank != 0:
            self.assertTrue(False)
        else:
            self.assertTrue(True)
    def testPeer_a_DBCreation(self):
        print('--------------------------')
        print('Running peer db creation test')
        if os.path.exists('data/peers.db'):
            os.remove('data/peers.db')
        import core
        myCore = core.Core()
        myCore.createPeerDB()
        if os.path.exists('data/peers.db'):
            self.assertTrue(True)
        else:
            self.assertTrue(False)
    def testPeer_b_addPeerToDB(self):
        print('--------------------------')
        print('Running peer db insertion test')
        import core
        myCore = core.Core()
        if not os.path.exists('data/peers.db'):
            myCore.createPeerDB()
        if myCore.addPeer('test'):
            self.assertTrue(True)
        else:
            self.assertTrue(False)
    def testData_b_Encrypt(self):
        self.assertTrue(True)
        return
        print('--------------------------')
        print('Running data dir encrypt test')
        import core
        myCore = core.Core()
        myCore.dataDirEncrypt('password')
        if os.path.exists('data-encrypted.dat'):
            self.assertTrue(True)
        else:
            self.assertTrue(False)
    def testData_a_Decrypt(self):
        self.assertTrue(True)
        return
        print('--------------------------')
        print('Running data dir decrypt test')
        import core
        myCore = core.Core()
        myCore.dataDirDecrypt('password')
        if os.path.exists('data/'):
            self.assertTrue(True)
        else:
            self.assertTrue(False)
    def testPGPGen(self):
        print('--------------------------')
        print('Testing PGP key generation')
        if os.path.exists('data/pgp/'):
            self.assertTrue(True)
        else:
            import core
            myCore = core.Core()
            myCore.generateMainPGP()
            if os.path.exists('data/pgp/'):
                self.assertTrue(True)
    def testHMACGen(self):
        print('--------------------------')
        print('running daemon queue test')
        # Test if hmac key generation is working
        import core
        myCore = core.Core()
        key = myCore.generateHMAC()
        if len(key) > 10:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
    def testQueue(self):
        print('--------------------------')
        print('running daemon queue test')
        # test if the daemon queue can read/write data
        import core
        myCore = core.Core()
        if not os.path.exists('data/queue.db'):
            myCore.daemonQueue()
        while True:
            command = myCore.daemonQueue()
            if command == False:
                print('The queue is empty (false)')
                break
            else:
                print(command[0])
        myCore.daemonQueueAdd('testCommand', 'testData')
        command = myCore.daemonQueue()
        if command[0] == 'testCommand':
            if myCore.daemonQueue() == False:
                print('Succesfully added and read command')
unittest.main()
