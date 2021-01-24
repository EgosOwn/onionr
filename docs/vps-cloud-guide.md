# Cloud/Server Hosting Onionr

Cloud hosting is not the recommended way to run Onionr, as it gives the cloud provider control over your data.

That said, it is quite useful and by running a 24/7 Onionr node you contribute to the network's health.

![https://cock.li/img/cockbox.png](https://cockbox.org/?r=12)

[Cockbox](https://cockbox.org/?r=12) is the recommended provider, as they do not demand personal information and accept Monero. This is an affiliate link, which gives us a commission at no expense or complication to you.


1. [Install Onionr like normal](./basic-onionr-user-guide.pdf) or [from Docker](./docker.md)
2. Run with specific host and port to bind to: `$ ./run-onionr-node.py --bind-address 0.0.0.0 --port 8080`
3. Get the web security token: `$ ./onionr.sh get-web` (the long string at the end of the URL)
4. [Configure Firefox for SSH tunneling](https://web.archive.org/web/20210123034529/https://gist.github.com/brentjanderson/6ed800376e53746d2d28ba7b6bdcdc12). `Set network.proxy.allow_hijacking_localhost` to true in about:config


Disable random host binding in config (general.security.random_bind_ip = false) if you have Onionr auto start. You may also want to disable deniable block inserts.