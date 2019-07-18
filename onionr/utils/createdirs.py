from . import identifyhome
import dbcreator, filepaths
home = identifyhome.identify_home()

if not os.path.exists(home):
    os.mkdir(home)
    os.mkdir(filepaths.block_data_location)

for db in dbcreator.create_funcs:
    try:
        db()
    except FileExistsError:
        pass