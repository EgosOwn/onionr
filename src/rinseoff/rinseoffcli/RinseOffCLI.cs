using System;
using System.IO;
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

namespace rinseoffcli
{
    class Program
    {
        public static string version = "2.0.0";
        enum ErrorCode : byte
        {
            // Exit error codes indexed from 1
            InvaildArgs = 1,
            NoDataFileFound,
            NoPermissionToReadDataFile,
            FailedToReadDataFile,
            FailedToWriteDataFile,
            InvalidKeyFileSize,
            InvalidKeyFile,
            KeyFileNotFound,
            NoPermissionToWriteKeyFile,
            FailedToReadKeyFile,
            FailedToWriteKeyFile
        }


        static void showHelp(ErrorCode exitCode = ErrorCode.InvaildArgs){
            Console.WriteLine("RinseOff " + version + " High level secure-erasure utility");
            Console.WriteLine("For stdout output, specify 'stdout' as the data file for the store command");
            Console.WriteLine("Must specify keygen <key path> or store/load, then a file name followed by a key file.\nFormat: <verb> <data file> <key file>");
            Environment.Exit((int) exitCode);
        }
        static void validateArgCount(string[] args, int count){
            if (args.Length != count){
                stderrWrite("Invalid number of arguments");
                showHelp(ErrorCode.InvaildArgs);
            }
        }
        static void stderrWrite(string msg){
            var stderrStream = Console.Error;
            stderrStream.WriteLine(msg);
            stderrStream.Flush();
        }

        static byte[] readUntilClose(){
            // Read binary from STDIN until close
            var readData = new List<byte>();
            Stream inputStream = Console.OpenStandardInput();
            int inp;
            while(true){
                inp = inputStream.ReadByte();
                if (inp != -1){
                    readData.Add((byte) inp);
                }
                else{
                    return readData.ToArray();
                }
            }
        }
        static void loadData(string filepath, string keypath){
            // Load in an encrypted file and use a key file to decrypt it, then log bytes back to stdout
            byte[] plaintext = {};
            byte[] ciphertext = {};
            byte[] readBytes(string file){
                // Read bytes in from a file, exit with error message if not possible
                byte[] bytesToRead = {};
                try{
                    bytesToRead = File.ReadAllBytes(file);
                }
                catch(FileNotFoundException){
                    stderrWrite(file + " is not found");
                    Environment.Exit((int)ErrorCode.NoDataFileFound);
                }
                catch(UnauthorizedAccessException){
                    stderrWrite("No permssion to read " + file);
                    Environment.Exit((int)ErrorCode.NoPermissionToReadDataFile);
                }
                catch(IOException){
                    stderrWrite("Failed to read " + file);
                    Environment.Exit((int)ErrorCode.FailedToReadDataFile);
                }
                return bytesToRead;
            }
            var stdout = Console.OpenStandardOutput();

            if (filepath.Equals("stdin")){
                ciphertext = readUntilClose();
            }
            else{
                ciphertext = readBytes(filepath);
            }
            try{
                // Decrypt a file using a key file
                plaintext = RinseOff.decrypt_secret_bytes(
                    ciphertext,
                    readBytes(keypath)
                );
            }
            catch(Sodium.Exceptions.KeyOutOfRangeException){
                stderrWrite("Keyfile is not appropriate size for key");
                Environment.Exit((int)ErrorCode.InvalidKeyFileSize);
            }
            catch(System.Security.Cryptography.CryptographicException){
                stderrWrite("Could not decrypt " + filepath + " with " + keypath);
                Environment.Exit((int)ErrorCode.InvalidKeyFile);
            }
            ciphertext = null;
            // print the plaintext and exit
            foreach(byte b in plaintext){
                stdout.WriteByte(b);
            }
            stdout.Flush();
        }

        static void storeData(string filepath, string keypath){
            byte[] encryptedInput = new byte[0];

            void writeStdoutBytes(byte[] data){
                var stdout = Console.OpenStandardOutput();
                foreach (byte b in data){
                    stdout.WriteByte(b);
                }
                stdout.Flush();
            }

            // Encrypt stdin with keyfile data then write out to output file
            try{
                encryptedInput = RinseOff.encrypt_secret_bytes(readUntilClose(), File.ReadAllBytes(keypath));
            }
            catch(FileNotFoundException){
                stderrWrite("Key file " + keypath + " does not exist");
                Environment.Exit((int)ErrorCode.KeyFileNotFound);
            }
            catch(Sodium.Exceptions.KeyOutOfRangeException){
                stderrWrite("Keyfile is not appropriate size for key");
                Environment.Exit((int)ErrorCode.InvalidKeyFileSize);
            }
            catch(IOException){
                stderrWrite("Failed to read key file " + keypath);
                Environment.Exit((int)ErrorCode.FailedToReadKeyFile);
            }
            if (filepath == "stdout"){
                writeStdoutBytes(encryptedInput);
                return;
            }
            try{
                File.WriteAllBytes(filepath, encryptedInput);
            }
            catch(ArgumentNullException)
            {
                Environment.Exit(0);
            }
            catch(DirectoryNotFoundException){
                stderrWrite("Output path " + filepath + " not found");
                Environment.Exit((int)ErrorCode.NoDataFileFound);
            }
            catch(IOException){
                stderrWrite("Could not write to " + filepath);
                Environment.Exit((int)ErrorCode.FailedToWriteDataFile);
            }
        }
        static void Main(string[] args)
        {
            if (args.Length == 0){
                showHelp();
            }
            var cmd = args[0].ToLower();
            switch(cmd){
                case "keygen":
                    validateArgCount(args, 2);
                    try{
                        RinseOff.generateKeyFile(args[1]);
                    }
                    catch(UnauthorizedAccessException){
                        stderrWrite("Cannot write to key file due to lack of perms " + args[1]);
                        Environment.Exit((int)ErrorCode.NoPermissionToWriteKeyFile);
                    }
                    catch(DirectoryNotFoundException){
                        stderrWrite("Path not found " + args[1]);
                        Environment.Exit((int)ErrorCode.KeyFileNotFound);
                    }
                    catch(IOException){
                        stderrWrite("Error writing keyfile " + args[1]);
                        Environment.Exit((int)ErrorCode.FailedToWriteKeyFile);
                    }
                break;
                case "store":
                    validateArgCount(args, 3);
                    storeData(args[1], args[2]);
                break;
                case "load":
                    validateArgCount(args, 3);
                    loadData(args[1], args[2]);
                break;
                default:
                    stderrWrite("Invalid command");
                    showHelp();
                break;
                case "help":
                case "--help":
                case "-h":
                showHelp();
                break;
            }
        }
    }
}
