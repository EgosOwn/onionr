import random, socket
import config, logger
def set_bind_IP(filePath=''):
    '''Set a random localhost IP to a specified file (intended for private or public API localhost IPs)'''

    if config.get('general.random_bind_ip', True):
        hostOctets = [str(127), str(random.randint(0x02, 0xFF)), str(random.randint(0x02, 0xFF)), str(random.randint(0x02, 0xFF))]
        data = '.'.join(hostOctets)
        # Try to bind IP. Some platforms like Mac block non normal 127.x.x.x
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((data, 0))
        except OSError:
            # if mac/non-bindable, show warning and default to 127.0.0.1
            logger.warn('Your platform appears to not support random local host addresses 127.x.x.x. Falling back to 127.0.0.1.')
            data = '127.0.0.1'
        s.close()
    else:
        data = '127.0.0.1'
    if filePath != '':
        with open(filePath, 'w') as bindFile:
            bindFile.write(data)
    return data