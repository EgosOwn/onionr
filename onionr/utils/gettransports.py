import filepaths

files = [filepaths.tor_hs_address_file]

def get():
        transports = []
        for file in files:
                try:
                        with open(file, 'r') as transport_file:
                                transports.append(transport_file.read())
                except FileNotFoundError:
                        transports.append('')
                        pass
        return list(transports)