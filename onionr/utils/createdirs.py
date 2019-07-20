import os
from . import identifyhome
import dbcreator, filepaths
home = identifyhome.identify_home()

def create_dirs():
    if not os.path.exists(home):
        os.mkdir(home)
    if not os.path.exists(filepaths.block_data_location):
        os.mkdir(filepaths.block_data_location)

    for db in dbcreator.create_funcs:
        try:
            db()
        except FileExistsError:
            pass