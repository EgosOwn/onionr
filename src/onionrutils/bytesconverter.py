def str_to_bytes(data: str) -> bytes:
    '''Convert a string to bytes with .encode(), utf8'''
    try:
        data = data.encode('UTF-8')
    except AttributeError:
        pass
    return data


def bytes_to_str(data: bytes) -> str:
    """Convert bytes to strings with .decode(), utf8"""
    try:
        data = data.decode('UTF-8')
    except AttributeError:
        pass
    return data
