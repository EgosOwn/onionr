import requests

from lan.getip import best_ip

def test_lan_server(testmanager):

    for i in range(1024, 65536):
        try:
            if requests.get(f"http://{best_ip}:{i}/ping").text == 'pong!':
                break
        except requests.exceptions.ConnectionError:
            pass
    else:
        raise ValueError