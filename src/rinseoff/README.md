<h1 align="center">RinseOff</h1>

RinseOff is a simple CLI utility written in C# to store data to a file and encrypt it using a keyfile.

The name doesn't make a lot of sense, but it means you can "rinse" your data off by just overwriting a 32 byte key file instead of the normal "scrub" process of 1 or more passes over many files.

It is mainly intended for scripts/apps to use. In the future I may make a FUSE wrapper so users can drop files into it.

Internally it uses libsodium's secretbox and stores a unique nonce alongside the 32 byte key.

# Build

Build a standalone binary (change [runtime based on system](https://docs.microsoft.com/en-us/dotnet/core/rid-catalog)):

`$ dotnet publish -p:PublishSingleFile=true --self-contained --runtime linux-x64`

The binary will be somewhere like bin/Debug/[dotnet version]/[runtime version]/publish/rinseoffcli

You can make a smaller binary by not bundling the runtime.

Or you can just "run" the project file: `$ dotnet run --project rinseoffcli`

# Usage

## Generate your key file

`$ rinseoffcli keygen /path/to/key`

Store your key somewhere it can be securely erased (not flash storage if you can help it) [security.stackexchange.com/a/62591](https://security.stackexchange.com/a/62591)

Be sure to make it accessible only to your user.

## Encrypt your data

`$ rinseoffcli store /path/to/output /path/to/key`

Then input the data to store through stdin.

## Load your data

`$ rinseoffcli load /path/to/stored/data /path/to/key`

If the key is valid, the plaintext will be outputted through stdout.
if data path is "stdin" it will be read from pipe according

## Securely erase data

`$ shred /path/to/key`
`$ rm /path/to/datafile`


# Warnings:

The point of this utility is to help with defense in depth and to be better than nothing.

**This does not hold up to serious data recovery experts who could quite possibly recover your key file**

If the OS pages or swaps your plaintext or duplicates your key, you are probably doomed.

