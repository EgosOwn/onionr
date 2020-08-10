"""Onionr - Private P2P Communication.

This file primarily serves to allow specific fetching of circles board messages
"""
from flask import Response, Blueprint, g

from deadsimplekv import DeadSimpleKV

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

flask_blueprint = Blueprint('debugAPI', __name__)


@flask_blueprint.route('/debug/dump_shared_state')
def get_shared_state() -> Response:
    """Return somewhat human-readable dump of shared toomanyobjects."""
    resp = ""
    for i in g.too_many.objects.keys:
        resp += i + dir(g.too_many.objects.keys[i]) + "\n"
    return Response(resp)


@flask_blueprint.route('/debug/dump_shared_vars')
def get_shared_vars() -> Response:
    """Return somewhat human-readable dump of pseudo globals (DeadSimpleKV)."""
    kv: DeadSimpleKV = g.too_many.get(DeadSimpleKV)
    resp = ""
    for i in kv.keys:
        resp += i + dir(g.too_many.objects.keys[i]) + "\n"
    return Response(resp)

