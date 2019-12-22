from gevent import time

import filepaths

files = [filepaths.tor_hs_address_file]


def get():
    transports = []
    for file in files:
        try:
            with open(file, 'r') as transport_file:
                transports.append(transport_file.read().strip())
        except FileNotFoundError:
            pass
        else:
            break
    else:
        time.sleep(1)
    return list(transports)
