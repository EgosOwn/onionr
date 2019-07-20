import hmac
def safe_compare(one, two):
    # Do encode here to avoid spawning core
    try:
        one = one.encode()
    except AttributeError:
        pass
    try:
        two = two.encode()
    except AttributeError:
        pass
    return hmac.compare_digest(one, two)