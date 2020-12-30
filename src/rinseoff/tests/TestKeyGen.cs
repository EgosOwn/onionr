using NUnit.Framework;
using System.IO;
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
namespace tests
{
    public class Tests
    {
        [SetUp]
        public void Setup()
        {
        }

        [Test]
        public void TestKeyGenBasic()
        {
            var f = Path.GetTempFileName();
            RinseOff.generateKeyFile(f);
            var k = File.ReadAllBytes(f);
            Assert.IsTrue(k.Length == 32);
            Assert.IsFalse(k[0] == k[1]);
            File.Delete(f);
        }
    }
}