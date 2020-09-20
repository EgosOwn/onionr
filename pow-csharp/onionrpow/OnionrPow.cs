using System;
using System.Text;
using SHA3;
using System.Linq;
using System.Collections.Generic;

namespace onionrpow
{
    public class OnionrPow
    {
        public static void compute(byte[] data, int difficulty){
            using (var shaAlg = SHA3.Net.Sha3.Sha3256())
            {
                // Replace beginning json with counter
                int counter = 0;
                var copy = new List<byte>();

                foreach(byte co in data){
                    if (counter < 1){
                        counter += 1;
                        continue;
                        //copy.Add(Encoding.UTF8.GetBytes("{\"pow\": "))
                    }
                    counter += 1;
                    copy.Add(co);
                }
                int c = 0;
                var copy2 = new List<byte>();
                while (true){
                    toploop:
                    c += 1;
                    var num = Encoding.UTF8.GetBytes("{\"pow\": " + c.ToString() + ",");
                    copy2.Clear();
                    copy2.AddRange(num);
                    copy2.AddRange(copy);
                    var hash = shaAlg.ComputeHash(copy2.ToArray());

                    int counter2 = 0;
                    foreach(byte one in hash){
                        if ((int) one != 0){
                            goto toploop;
                        }
                        counter2 += 1;
                        if (counter2 == difficulty){
                            break;
                        }
                    }
                    Console.WriteLine(Encoding.UTF8.GetString(copy2.ToArray()));
                    Console.WriteLine(BitConverter.ToString(hash));
                    Console.WriteLine(c);
                    break;
               }
            }
        }
        //b'{"meta":"{\\"ch\\":\\"global\\",\\"type\\":\\"brd\\"}","sig":"pR4qmKGGCdnyNyZRlhGfF9GC7bONCsEnY04lTfiVuTHexPJypOqmxe9iyDQQqdR+PB2gwWuNqGMs5O8\\/S\\/hsCA==","signer":"UO74AP5LGQFI7EJTN6NAVINIPU2XO2KA7CAS6KSWGWAY5XIB5SUA====","time":1600542238,"pow":300182}\nxcvxcvvxcxcv'
    }
}
