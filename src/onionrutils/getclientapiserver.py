'''
    Onionr - Private P2P Communication

    Return the client api server address and port, which is usually random
'''
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
import filepaths
import config
def get_client_API_server():
    config.reload()
    retData = ''
    getconf = lambda: config.get('client.client.port')
    port = getconf()
    if port is None:
        config.reload()
        port = getconf()
    try:
        with open(filepaths.private_API_host_file, 'r') as host:
            hostname = host.read()
    except FileNotFoundError:
        raise FileNotFoundError
    else:
        retData += '%s:%s' % (hostname, port)
    return retData
