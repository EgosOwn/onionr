from time import sleep


def better_sleep(wait: int):
    """Sleep catching ctrl c for wait seconds."""
    try:
        sleep(wait)
    except KeyboardInterrupt:
        pass

