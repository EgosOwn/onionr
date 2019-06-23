import requests
import logger, onionrexceptions
from onionr import API_VERSION
def do_post_request(utils_inst, url, data={}, port=0, proxyType='tor'):
    '''
    Do a POST request through a local tor or i2p instance
    '''
    if proxyType == 'tor':
        if port == 0:
            port = utils_inst._core.torPort
        proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
    elif proxyType == 'i2p':
        proxies = {'http': 'http://127.0.0.1:4444'}
    else:
        return
    headers = {'user-agent': 'PyOnionr', 'Connection':'close'}
    try:
        proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
        r = requests.post(url, data=data, headers=headers, proxies=proxies, allow_redirects=False, timeout=(15, 30))
        retData = r.text
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except requests.exceptions.RequestException as e:
        logger.debug('Error: %s' % str(e))
        retData = False
    return retData

def do_get_request(utils_inst, url, port=0, proxyType='tor', ignoreAPI=False, returnHeaders=False):
    '''
    Do a get request through a local tor or i2p instance
    '''
    retData = False
    if proxyType == 'tor':
        if port == 0:
            raise onionrexceptions.MissingPort('Socks port required for Tor HTTP get request')
        proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
    elif proxyType == 'i2p':
        proxies = {'http': 'http://127.0.0.1:4444'}
    else:
        return
    headers = {'user-agent': 'PyOnionr', 'Connection':'close'}
    response_headers = dict()
    try:
        proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
        r = requests.get(url, headers=headers, proxies=proxies, allow_redirects=False, timeout=(15, 30), )
        # Check server is using same API version as us
        if not ignoreAPI:
            try:
                response_headers = r.headers
                if r.headers['X-API'] != str(API_VERSION):
                    raise onionrexceptions.InvalidAPIVersion
            except KeyError:
                raise onionrexceptions.InvalidAPIVersion
        retData = r.text
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except ValueError as e:
        pass
    except onionrexceptions.InvalidAPIVersion:
        if 'X-API' in response_headers:
            logger.debug('Using API version %s. Cannot communicate with node\'s API version of %s.' % (API_VERSION, response_headers['X-API']))
        else:
            logger.debug('Using API version %s. API version was not sent with the request.' % API_VERSION)
    except requests.exceptions.RequestException as e:
        if not 'ConnectTimeoutError' in str(e) and not 'Request rejected or failed' in str(e):
            logger.debug('Error: %s' % str(e))
        retData = False
    if returnHeaders:
        return (retData, response_headers)
    else:
        return retData