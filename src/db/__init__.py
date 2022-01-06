import dbm
import time
import os

timeout = 120


def _do_timeout(func, *args):
    ts = 0
    res = None
    while True:
        try:
            res = func(*args)
        except dbm.error:
            if not ts:
                ts = time.time()
                continue
            if time.time() - ts > timeout:
                raise TimeoutError()
            time.sleep(0.1)
        else:
            return res


def set(db_path, key, value):
    def _set(key, value):
        with dbm.open(db_path, "c") as my_db:
            my_db[key] = value
    _do_timeout(_set, key, value)


def get(db_path, key):
    def _get(key):
        with dbm.open(db_path, "c") as my_db:
            return my_db[key]
    return _do_timeout(_get, key)

