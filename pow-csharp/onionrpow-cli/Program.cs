using System;
using System.Text;

using onionrpow;

namespace onionrpow_cli
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello World!");
            onionrpow.OnionrPow.compute(Encoding.UTF8.GetBytes("test"), 4);
        }
    }
}
