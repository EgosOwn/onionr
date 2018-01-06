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
import unittest, sys, os

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
    def testPGPGen(self):
        print('--------------------------')
        print('Testing PGP key generation')
        if os.path.exists('data/pgp/'):
            self.assertTrue(False)
        else:
            import core
            myCore = core.Core()
            myCore.generateMainPGP()
            if os.path.exists('data/pgp/'):
                self.assertTrue(True)
    def testQueue(self):
        print('--------------------------')
        print('running daemon queue test')
        # test if the daemon queue can read/write data
        import core
        myCore = core.Core()
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