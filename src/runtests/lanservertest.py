import requests

from lan.getip import best_ip

from onionrblocks import insert, onionrblockapi

def test_lan_server(testmanager):

    for i in range(1024, 65536):
        try:
            if requests.get(f"http://{best_ip}:{i}/ping").text == 'pong!':
                bl = insert('test data')
                bl2 = insert('test data2')
                l = requests.get(f"http://{best_ip}:{i}/blist/0").text
                if bl not in l or bl2 not in l:
                    raise ValueError
                if onionrblockapi.Block(bl).raw != requests.get(f"http://{best_ip}:{i}/get/{bl}").content:
                    raise ValueError
                
                break

        except requests.exceptions.ConnectionError:
            pass
    else:
        raise ValueError