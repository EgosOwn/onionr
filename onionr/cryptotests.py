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
import unittest, sys, os, core, onionrcrypto, logger

class OnionrCryptoTests(unittest.TestCase):
    def testSymmetric(self):
        dataString = "this is a secret message"
        dataBytes = dataString.encode()
        myCore = core.Core()
        crypto = onionrcrypto.OnionrCrypto(myCore)
        key = key = b"tttttttttttttttttttttttttttttttt"

        logger.info("Encrypting: " + dataString, timestamp=True)
        encrypted = crypto.symmetricEncrypt(dataString, key, returnEncoded=True)
        logger.info(encrypted, timestamp=True)
        logger.info('Decrypting encrypted string:', timestamp=True)
        decrypted = crypto.symmetricDecrypt(encrypted, key, encodedMessage=True)
        logger.info(decrypted, timestamp=True)
        self.assertTrue(True)
if __name__ == "__main__":
    unittest.main()
