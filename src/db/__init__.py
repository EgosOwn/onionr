import dbm
import time
import os

timeout = 120

class DuplicateKey(ValueError): pass


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
            time.sleep(0.01)
        else:
            return res


def set_if_new(db_path, key, value):
    def _set(key, value):
        with dbm.open(db_path, "c") as my_db:
            try:
                my_db[key]
            except KeyError:
                my_db[key] = value
            else:
                raise DuplicateKey
    _do_timeout(_set, key, value)


def set(db_path, key, value):
    """Set a value in the db, open+timeout so not good for rapid use"""
    def _set(key, value):
        with dbm.open(db_path, "c") as my_db:
            my_db[key] = value
    _do_timeout(_set, key, value)


def get(db_path, key):
    """Get a value in the db, open+timeout so not good for rapid use"""
    def _get(key):
        with dbm.open(db_path, "cu") as my_db:
            return my_db[key]
    return _do_timeout(_get, key)



def get_db_obj(db_path, extra_flag=''):
    """For when you should keep a db obj open"""
    def _get_db():
        return dbm.open(db_path, "c" + extra_flag)
    return _do_timeout(_get_db)


def list_keys(db_path):
    """Generator of all keys in the db.

    Uses a lot of mem if no firstkey supported"""
    db_obj = _do_timeout(dbm.open, db_path, "cu")
    if not hasattr(db_obj, "firstkey"):
        for i in db_obj.keys():
            yield i
        db_obj.close()
        return


    def _list_keys(db_obj):
        with db_obj as my_db:
            k = my_db.firstkey()
            while k is not None:
                yield k
                k = my_db.nextkey(k)
    yield from _list_keys(db_obj)

