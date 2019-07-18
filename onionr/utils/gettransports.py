import filepaths

files = [filepaths.tor_hs_address_file]
transports = []
for file in files:
        with open(file, 'r') as transport_file:
                transports.append(transport_file.read())