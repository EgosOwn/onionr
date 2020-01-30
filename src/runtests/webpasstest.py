import requests

from onionrutils import localcommand


def webpass_test(test_manager):
    if requests.get('http://' + localcommand.get_hostname() + '/ping') == \
        'pong!':
        raise ValueError
    if localcommand.local_command('ping') != 'pong!':
        raise ValueError('Could not ping with normal localcommand in webpasstest')
