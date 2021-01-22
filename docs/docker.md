# Running Onionr in Docker

A Dockerfile is included in the root directory of Onionr.

In Docker version 20.10 (and probably others), there is a strange bug where Onionr must be run with -it or stdout will be garbled and it may hang.

## Clone and build the image

`$ git clone https://git.voidnet.tech/kev/onionr/`
`$ cd onionr`
`$ sudo docker build -t onionr .`


## Run Onionr

`$ sudo docker run -it -p 8080:8080 onionr`

Onionr will be accessible over any network interface by default, so make sure to either change the entry point bind-address argument or set a firewall rule.

That said, Onionr does protect it's interface by default with a web token, which will be shown in stdout.

**However, anyone who can access the port may be able to see what Onionr sites you have saved and potentially deanonymize your node**

## View the UI

Visit the address and port for the machine Onionr is running on, for example: http://192.168.1.5:8080/#<long-token-taken-from-stdout>

If you want a secure connection to the interface, either use a proxy such as nginx or caddy, or use [SSH tunneling](./vps-cloud-guide.md).
