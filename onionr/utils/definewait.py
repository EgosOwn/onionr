import time
def define_wait(dictionary, key, delay: int = 0):
    while True:
        try:
            return dictionary[key]
        except KeyError:
            pass
        if delay > 0:
            time.sleep(delay)