using System;
using System.Text;
using System.Linq;
using System.Collections.Generic;
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

                var justDataArray = justData.ToArray();
                justData.Clear();
                var encoded = new List<byte>();
                int calculatedDifficulty = 0;

                var nl = Encoding.UTF8.GetBytes("\n")[0];

                while(true){
                    encoded.Clear();
                    encoded.AddRange(Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(block)));
                    // TODO keep nl and dataarray in
                    encoded.Add(nl);
                    encoded.AddRange(justDataArray);
                    var encodedArray = encoded.ToArray();

                    calculatedDifficulty = 0;

                    foreach(char c in shaAlg.ComputeHash(encodedArray)){
                        if (c == 0){
                            calculatedDifficulty += 1;
                            if (calculatedDifficulty == difficulty){
                                Console.WriteLine(counter);
                                Console.WriteLine(Encoding.UTF8.GetString(encodedArray));
                                Console.WriteLine(BitConverter.ToString(shaAlg.ComputeHash(encodedArray)));

                                goto powDone;
                            }
                        }
                        else{
                            break;
                        }
                    }

                    block.c += 1;
                }
            }
            powDone:;
        }
        //b'{"meta":"{\\"ch\\":\\"global\\",\\"type\\":\\"brd\\"}","sig":"pR4qmKGGCdnyNyZRlhGfF9GC7bONCsEnY04lTfiVuTHexPJypOqmxe9iyDQQqdR+PB2gwWuNqGMs5O8\\/S\\/hsCA==","signer":"UO74AP5LGQFI7EJTN6NAVINIPU2XO2KA7CAS6KSWGWAY5XIB5SUA====","time":1600542238,"pow":300182}\nxcvxcvvxcxcv'
    }
}
