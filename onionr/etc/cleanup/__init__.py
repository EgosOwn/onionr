import os, filepaths
def delete_run_files():
    try:
        os.remove(filepaths.public_API_host_file)
    except FileNotFoundError:
        pass
    try:
        os.remove(filepaths.private_API_host_file)
    except FileNotFoundError:
        pass