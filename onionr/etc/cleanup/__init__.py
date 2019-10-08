import os, filepaths

def _safe_remove(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

def delete_run_files():
     _safe_remove(filepaths.public_API_host_file)
     _safe_remove(filepaths.private_API_host_file)
     _safe_remove(filepaths.daemon_mark_file)
     _safe_remove(filepaths.lock_file)
