import filepaths, time

files = [filepaths.tor_hs_address_file]

def get():
        transports = []
        while len(transports) == 0:
                for file in files:
                        try:
                                with open(file, 'r') as transport_file:
                                        transports.append(transport_file.read().strip())
                        except FileNotFoundError:
                                transports.append('')
                        else:
                                break
                else:
                        time.sleep(1)
        return list(transports)