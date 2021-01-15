# Generating requirements.txt

To generate a requirements.txt file, install pip-tools from pip

Onionr requirements files should have hashes to prevent backdooring by the pypi server.

Put your package versions in requirements.in like normal. Child dependencies are usually not necessary:

```
requests==0.1.1
flask==0.1.1
```

Then generate the requirements.txt:

`$ pip-compile requirements.in --generate-hashes -o requirements.txt`


Your requirements.txt will have hash-pinned requirements of all dependencies and child dependencies.
