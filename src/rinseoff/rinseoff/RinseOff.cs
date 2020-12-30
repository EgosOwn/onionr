using System;
using Sodium;
using System.IO;
using System.Collections.Generic;

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

namespace rinseoff
{
    public class RinseOff
    {
        public static void generateKeyFile(string path){
            var key = Sodium.SodiumCore.GetRandomBytes(32);
            File.WriteAllBytes(path, key);
        }

        public static byte[] encrypt_secret_bytes(byte[] secret, byte[] key){
            byte[] nonce = Sodium.SecretBox.GenerateNonce();
            var ciphertext = SecretBox.Create(secret, nonce, key);
            var combined = new List<byte>();
            combined.AddRange(nonce);
            combined.AddRange(ciphertext);
            return combined.ToArray();
        }

        public static byte[] decrypt_secret_bytes(byte[] ciphertext, byte[] key){
            var ciphertextList = new List<byte>();
            ciphertextList.AddRange(ciphertext);
            return Sodium.SecretBox.Open(
                ciphertextList.GetRange(24, ciphertextList.Count - 24).ToArray(),
                ciphertextList.GetRange(0, 24).ToArray(),
                key);
        }


    }
}
