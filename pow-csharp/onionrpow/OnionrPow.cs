using System;
using System.Text;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using Newtonsoft.Json;
using SHA3;

namespace onionrpow
{

    public class Meta{
        public string ch { get; set; }
        public string type { get; set; }
    }

    public class Block{
        public string meta { get; set; }
        public string sig { get; set; }
        public string signer { get; set; }

        public int n;
        public int c;
        public int time;

        //public List<byte> data { get; set; }

    }
    public class OnionrPow
    {
        public static void compute(byte[] data, int difficulty){
            using (var shaAlg = SHA3.Net.Sha3.Sha3256())
            //using (SHA256 shaAlg = SHA256.Create())
            {
                string stringData = Encoding.UTF8.GetString(data);
                bool found = false;
                var justData = new List<byte>();
                var metadataJson = new List<byte>();
                int counter = 0;
                foreach(char c in stringData){
                    if (found){
                        justData.Add((byte) c);
                    }
                    else if (c == '\n'){
                        for (int i = 0; i < counter + 1; i++){
                            metadataJson.Add(data[i]);
                        }
                        found = true;
                    }
                    else{
                        //Console.WriteLine(c.ToString());
                    }
                    counter += 1;
                }
                Block block = JsonConvert.DeserializeObject<Block>(Encoding.UTF8.GetString(metadataJson.ToArray()));
                block.n = new Random().Next(10000);
                block.c = 0;

                metadataJson.Clear();
                metadataJson.AddRange(Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(block)));
                int location = Encoding.UTF8.GetString(metadataJson.ToArray()).IndexOf("\"c\":");

                var metadata1 = new List<byte>();
                var metadata2 = new List<byte>();
                var countKey = new List<byte>();
                countKey.AddRange(Encoding.UTF8.GetBytes("\"c\":"));

                bool afterNum = false;
                for (int i = location + 4; i < metadataJson.Count; i++){
                    if (!afterNum && ((char) metadataJson[i]).Equals(',')){
                        afterNum = true;
                        continue;
                    }
                    if (afterNum){
                        metadata2.Add(metadataJson[i]);
                    }
                }
                for (int i = 0; i < location; i++){
                    metadata1.Add(metadataJson[i]);
                }

                var preCompiled = new List<byte>();
                preCompiled.AddRange(metadata1);
                preCompiled.AddRange(countKey);
                int powCounter = 0;

                var justDataArray = justData.ToArray();
                justData.Clear();
                int difficultyCounter = 0;
                while(true){
                    var compiled = preCompiled.ToList();
                    compiled.AddRange(metadata1);
                    compiled.AddRange(Encoding.UTF8.GetBytes(powCounter.ToString()));
                    compiled.AddRange(metadata2);
                    compiled.AddRange(justDataArray);
                    var hash = shaAlg.ComputeHash(compiled.ToArray());
                    foreach (byte b in hash){
                        if (b == 0){
                            difficultyCounter += 1;
                            if (difficultyCounter == difficulty){
                                Console.WriteLine(powCounter);
                                Console.WriteLine(BitConverter.ToString(hash));
                                goto powDone;
                            }
                            continue;
                        }
                        difficultyCounter = 0;
                        break;
                    }
                    //Console.WriteLine(powCounter);
                    powCounter += 1;
                }




                //Console.WriteLine(location);
                //Console.WriteLine(Encoding.UTF8.GetString(metadataJson.ToArray()));
            }
            powDone:;
        }
        //b'{"meta":"{\\"ch\\":\\"global\\",\\"type\\":\\"brd\\"}","sig":"pR4qmKGGCdnyNyZRlhGfF9GC7bONCsEnY04lTfiVuTHexPJypOqmxe9iyDQQqdR+PB2gwWuNqGMs5O8\\/S\\/hsCA==","signer":"UO74AP5LGQFI7EJTN6NAVINIPU2XO2KA7CAS6KSWGWAY5XIB5SUA====","time":1600542238,"pow":300182}\nxcvxcvvxcxcv'
    }
}
