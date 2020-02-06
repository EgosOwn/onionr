import platform

from onionrutils import localcommand


def test_os_ver_endpoint(test_manager):
    if localcommand.local_command('os') != platform.system().lower():
        raise ValueError('could not get proper os platform from endpoint /os')
