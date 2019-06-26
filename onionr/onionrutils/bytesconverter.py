def str_to_bytes(data):
    '''Converts a string to bytes with .encode()'''
    try:
        data = data.encode('UTF-8')
    except AttributeError:
        pass
    return data

def bytes_to_str(data):
    try:
        data = data.decode('UTF-8')
    except AttributeError:
        pass
    return data