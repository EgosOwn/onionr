using System;
using System.Text;
using System.IO;
using System.Collections.Generic;

using onionrpow;

namespace onionrpow_cli
{
    class Program
    {
        static void Main(string[] args)
        {

            TimeSpan t = DateTime.UtcNow - new DateTime(1970, 1, 1);
            int secondsSinceEpoch = (int)t.TotalSeconds;
            using (Stream stdin = Console.OpenStandardInput())
            {
                var data = new List<byte>();
                byte[] buffer = new byte[60000];
                int bytes;
                while ((bytes = stdin.Read(buffer, 0, buffer.Length)) > 0) {
                    //stdout.Write(buffer, 0, bytes);
                    data.AddRange(buffer);
                }
                onionrpow.OnionrPow.compute(data.ToArray(), 2);
            }
            TimeSpan t2 = DateTime.UtcNow - new DateTime(1970, 1, 1);
            Console.WriteLine((int)t2.TotalSeconds - secondsSinceEpoch);
        }
    }
}
