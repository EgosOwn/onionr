"""
    Onionr - Private P2P Communication

    send a command to the local API server
"""
import urllib, time
import json
import functools
from typing import TYPE_CHECKING, Callable

import requests

import logger, config, deadsimplekv
from . import getclientapiserver
import filepaths
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
config.reload()

cache = deadsimplekv.DeadSimpleKV(filepaths.cached_storage, refresh_seconds=1000)
def get_hostname():
    hostname = ''
    waited = 0
    maxWait = 3
    while True:
        if cache.get('client_api') is None:
            try:
                hostname = getclientapiserver.get_client_API_server()
            except FileNotFoundError:
                hostname = False
            else:
                cache.put('hostname', hostname)
                cache.flush()
        else:
            hostname = cache.get('hostname')
        if hostname == '' or hostname is None:
            time.sleep(1)
            if waited == maxWait:
                return False
        else:
            return hostname

def local_command(command, data='', silent = True, post=False,
                  postData = {}, maxWait=20,
                  is_json=False
                  ):
    """
        Send a command to the local http API server, securely. Intended for local clients, DO NOT USE for remote peers.
    """
    # TODO: URL encode parameters, just as an extra measure. May not be needed, but should be added regardless.
    hostname = get_hostname()
    if hostname == False: return False

    if data != '':
        data = '&data=' + urllib.parse.quote_plus(data)
    payload = 'http://%s/%s%s' % (hostname, command, data)

    try:
        if post:
            if is_json:
                ret_data = requests.post(
                    payload,
                    json=postData,
                    headers={'token': config.get('client.webpassword'),
                             'Connection': 'close'},
                    timeout=(maxWait, maxWait)).text
            else:
                ret_data = requests.post(
                    payload,
                    data=postData,
                    headers={'token': config.get('client.webpassword'),
                             'Connection': 'close'},
                    timeout=(maxWait, maxWait)).text
        else:
            ret_data = requests.get(payload, headers={'token': config.get('client.webpassword'), 'Connection':'close'}, timeout=(maxWait, maxWait)).text
    except Exception as error:
        if not silent:
            logger.error('Failed to make local request (command: %s):%s' % (command, error), terminal=True)
        ret_data = False

    return ret_data
