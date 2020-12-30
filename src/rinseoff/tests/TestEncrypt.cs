using NUnit.Framework;
using System.Text;
using System.Collections.Generic;
using rinseoff;
/*
    RinseOff - Encrypt or load data with a key file to help with secure erasure
    Copyright (C) <2020>  Kevin Froman

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/
namespace testEncrypted
{
    public class Tests
    {
        [SetUp]
        public void Setup()
        {
        }

        [Test]
        public void TestEncrypt()
        {
            var key = Sodium.SecretBox.GenerateKey();
            var secret = Encoding.UTF8.GetBytes("Hello world");
            var encrypted = RinseOff.encrypt_secret_bytes(secret, key);
            var encryptedList = new List<byte>();
            encryptedList.AddRange(encrypted);

            Assert.AreNotEqual(secret, encrypted);
            var nonce = encryptedList.GetRange(0, 24).ToArray();
            var cipher = encryptedList.GetRange(24, encryptedList.Count - 24).ToArray();

            var decrypted = Sodium.SecretBox.Open(cipher, nonce, key);
            Assert.AreEqual(decrypted, secret);

        }
    }
}