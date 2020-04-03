"""
    Onionr - Private P2P Communication

    This file handles configuration setting and getting from the HTTP API
"""
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
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from json import JSONDecodeError
import ujson as json
from flask import Blueprint, request, Response, abort

import config, onionrutils

from onionrutils.bytesconverter import bytes_to_str
config.reload()

config_BP = Blueprint('config_BP', __name__)

@config_BP.route('/config/get')
def get_all_config():
    """Simply return all configuration as JSON string"""
    return Response(json.dumps(config.get_config(), indent=4, sort_keys=True))

@config_BP.route('/config/get/<key>')
def get_by_key(key):
    """Return a config setting by key"""
    return Response(json.dumps(config.get(key)))

@config_BP.route('/config/setall', methods=['POST'])
def set_all_config():
    """Overwrite existing JSON config with new JSON string"""
    try:
        new_config = request.get_json(force=True)
    except JSONDecodeError:
        abort(400)
    else:
        config.set_config(new_config)
        config.save()
        return Response('success')

@config_BP.route('/config/set/<key>', methods=['POST'])
def set_by_key(key):
    """Overwrite/set only 1 config key"""
    """
    {
        'data': data
    }
    """
    try:
        data = json.loads(bytes_to_str(request.data))
    except (JSONDecodeError, KeyError):
        abort(400)
    config.set(key, data, True)
    return Response('success')