import os
def read_static(file, ret_bin=False):
    static_file = os.path.realpath(__file__) + '../static-data/' + file

    if ret_bin:
        mode = 'rb'
    else:
        mode = 'r'
    with open(static_file, mode) as f:
        return f.read()