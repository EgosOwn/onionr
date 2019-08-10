import os
def get_static_dir():
    return os.path.dirname(os.path.realpath(__file__)) + '/../static-data/'
def read_static(file, ret_bin=False):
    static_file = get_static_dir() + file

    if ret_bin:
        mode = 'rb'
    else:
        mode = 'r'
    with open(static_file, mode) as f:
        data = f.read()
    return data