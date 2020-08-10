import requests

from lan.getip import best_ip

from onionrblocks import insert, onionrblockapi
from gevent import sleep
from coredb import blockmetadb
from onionrutils.epoch import get_epoch
import logger
from etc import onionrvalues

def test_lan_server(testmanager):
    if onionrvalues.IS_QUBES:
        logger.warn("Cannot test LAN on QubesOS", terminal=True)
        return
    start_time = get_epoch()
    for i in range(1337, 1340):
        try:
            if not best_ip or not best_ip.startswith(('192.168')):
                logger.warn(
                    "lanservertest not running, not in standard 192.168 lan " +
                    "run this test on a lan before release",
                    terminal=True)
                return
            if requests.get(f"http://{best_ip}:{i}/ping").text == 'onionr!':
                bl = insert('test data')
                sleep(10)
                bl2 = insert('test data2')
                sleep(30)
                bl3 = insert('test data3')
                l = requests.get(f"http://{best_ip}:{i}/blist/0").text.split('\n')
                if bl not in l or bl2 not in l or bl3 not in l:
                    logger.error('blocks not in blist ' + '-'.join(l))
                    raise ValueError
                time = blockmetadb.get_block_date(bl3) - 1
                l = requests.get(f"http://{best_ip}:{i}/blist/{time}").text.split('\n')

                if (bl in l and bl2 in l and bl3 in l) or len(l) == 0:
                    logger.error('Failed to get appopriate time' + '-'.join(l))
                    raise ValueError
                if onionrblockapi.Block(bl).raw != requests.get(f"http://{best_ip}:{i}/get/{bl}", stream=True).raw.read(6000000):
                    logger.error('Block doesn\'t match')
                    raise ValueError

                break

        except requests.exceptions.ConnectionError:
            pass
    else:
        raise ValueError