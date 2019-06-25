def str_to_bytes(data):
    try:
        data = data.encode()
    except AttributeError:
        pass
    return data

def bytes_to_str(data):
    try:
        data = data.decode()
    except AttributeError:
        pass
    return data