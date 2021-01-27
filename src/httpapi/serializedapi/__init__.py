"""Onionr - Private P2P Communication.

view and interact with onionr sites
"""
from flask import Blueprint, Response, request, abort, g
import json
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


serialized_api_bp = Blueprint('serializedapi', __name__)


@serialized_api_bp.route(
    '/serialized/<name>', endpoint='serialized', methods=['POST'])
def serialized(name: str) -> Response:
    initial = g.too_many.get_by_string(name.split('.')[0])
    for c, i in enumerate(name.split('.')):
        if i and c != 0:
            attr = getattr(initial, i)

    if callable(attr):
        try:
            js = request.get_json(force=True)
            print('json', js, type(js))
            data = json.loads(js)
            args = data['args']
            del data['args']
        except (TypeError, ValueError) as e:
            print(repr(e))
            data = {}
            args = []
        print('data', data)
        if data:
            print(*args, **data)
            resp = attr(*args, **data)
            if isinstance(resp, int):
                resp = str(resp)
            return Response(resp)
        else:
            print(*args, **data)
            resp = attr(*args)
            if isinstance(resp, int):
                resp = str(resp)
            return Response(resp, content_type='application/octet-stream')
    else:
        if isinstance(attr, int):
            attr = str(attr)
        return Response(attr, content_type='application/octet-stream')

