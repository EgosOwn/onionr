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
        public int time;

        private List<byte> data;

        public void setData(List<byte> blockData){
            this.data = blockData;
        }

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
                block.setData(justData);

            }
        }
        //b'{"meta":"{\\"ch\\":\\"global\\",\\"type\\":\\"brd\\"}","sig":"pR4qmKGGCdnyNyZRlhGfF9GC7bONCsEnY04lTfiVuTHexPJypOqmxe9iyDQQqdR+PB2gwWuNqGMs5O8\\/S\\/hsCA==","signer":"UO74AP5LGQFI7EJTN6NAVINIPU2XO2KA7CAS6KSWGWAY5XIB5SUA====","time":1600542238,"pow":300182}\nxcvxcvvxcxcv'
    }
}
