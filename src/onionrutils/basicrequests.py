'''Onionr - Private P2P Communication.

    Do HTTP GET or POST requests through a proxy
'''
from ipaddress import IPv4Address
from urllib.parse import urlparse

import requests, streamedrequests
import logger, onionrexceptions
from etc import onionrvalues
from . import localcommand
'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


def do_post_request(url, data={}, port=0, proxyType='tor', max_size=10000, content_type: str = ''):
    '''Do a POST request through a local tor or i2p instance.'''
    if proxyType == 'tor':
        if port == 0:
            port = localcommand.local_command('/gettorsocks')
        proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
    elif proxyType == 'i2p':
        proxies = {'http': 'http://127.0.0.1:4444'}
    elif proxyType == 'lan':
        address = urlparse(url).hostname
        if IPv4Address(address).is_private and not IPv4Address(address).is_loopback:
            proxies = {}
        else:
            return
    else:
        return
    headers = {'User-Agent': 'PyOnionr', 'Connection':'close'}
    if len(content_type) > 0:
        headers['Content-Type'] = content_type
    try:
        proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
        #r = requests.post(url, data=data, headers=headers, proxies=proxies, allow_redirects=False, timeout=(15, 30))
        r = streamedrequests.post(url, post_data=data, request_headers=headers, proxy=proxies, connect_timeout=15, stream_timeout=30, max_size=max_size, allow_redirects=False)
        retData = r[1]
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except requests.exceptions.RequestException as e:
        logger.debug('Error: %s' % str(e))
        retData = False
    return retData


def do_get_request(url, port=0, proxyType='tor', ignoreAPI=False, returnHeaders=False, max_size=5242880, connect_timeout=15):
    '''
    Do a get request through a local tor or i2p instance
    '''
    API_VERSION = onionrvalues.API_VERSION
    retData = False
    if proxyType == 'tor':
        if port == 0:
            port = localcommand.local_command('/gettorsocks')
        proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
    elif proxyType == 'i2p':
        proxies = {'http': 'http://127.0.0.1:4444'}
    elif proxyType == 'lan':
        address = urlparse(url).hostname
        if IPv4Address(address).is_private and not IPv4Address(address).is_loopback:
            proxies = None
        else:
            return
    else:
        return
    headers = {'User-Agent': 'PyOnionr', 'Connection':'close'}
    response_headers = dict()
    try:
        if not proxies is None:
            proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
        r = streamedrequests.get(url, request_headers=headers, allow_redirects=False, proxy=proxies, connect_timeout=connect_timeout, stream_timeout=120, max_size=max_size)
        # Check server is using same API version as us
        if not ignoreAPI:
            try:
                response_headers = r[0].headers
                if r[0].headers['X-API'] != str(API_VERSION):
                    raise onionrexceptions.InvalidAPIVersion
            except KeyError:
                raise onionrexceptions.InvalidAPIVersion
        retData = r[1]
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
