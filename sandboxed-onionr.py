#!/usr/bin/env python3

import os, sys
import tempfile, shutil
import stat

env_var = "firejailed-onionr"

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        if item in (".git", ".vscode", ".github"):
            continue
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

env_var = "firejailed-onionr"
directory = os.path.dirname(os.path.realpath(sys.argv[0]))

if not os.getenv(env_var):
    temp_dir = tempfile.mkdtemp()
    print(temp_dir)
    copytree(directory, temp_dir)
    os.system(f"firejail --env={env_var}={temp_dir} --private={temp_dir} python3 ./sandboxed-onionr.py")
    sys.exit(0)

os.system(f"python3 -m pip install -r ./requirements.txt --user")
os.system(f"./onionr.sh start &")


