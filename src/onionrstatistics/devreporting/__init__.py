import config
from utils.bettersleep import better_sleep
from utils.gettransports import get as get_transports
from onionrutils import basicrequests
from onionrutils import epoch

import json

def statistics_reporter(shared_state):
    server = config.get('statistics.server', '')
    if not config.get('statistics.i_dont_want_privacy', False) or \
        not server: return

    def compile_data():
        return {
            'time': epoch.get_epoch(),
            'adders': get_transports(),
            'peers': shared_state.get_by_string('OnionrCommunicatorDaemon').onlinePeers
            }

    while True:
        better_sleep(5)
        data = compile_data()
        basicrequests.do_post_request(
            f'http://{server}/sendstats/' + get_transports()[0],
            data=json.dumps(data))
