import os
from . import identifyhome
import dbcreator, filepaths
home = identifyhome.identify_home()

def create_dirs():
    gen_dirs = [home, filepaths.block_data_location, filepaths.contacts_location, filepaths.export_location]
    for path in gen_dirs:
        if not os.path.exists(path):
            os.mkdir(path)

    for db in dbcreator.create_funcs:
        try:
            db()
        except FileExistsError:
            pass