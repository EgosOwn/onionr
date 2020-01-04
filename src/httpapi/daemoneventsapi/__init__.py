"""Onionr - Private P2P Communication.

Event driven interface to trigger events in communicator
"""
from typing import Callable

from flask import Blueprint, request, Response, abort
from werkzeug.exceptions import BadRequest
from gevent import spawn

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


class DaemonEventsBP:
    def __init__(self):
        """Create DaemonEvents instance, intended to be a singleton.

        Attributes:
        listeners: callables that are called when a new event is added.
            The callables name should match the event name
        _too_many: TooManyObjects instance set by external code
        """
        event_BP = Blueprint('event_BP', __name__)
        self.listeners = set([])
        self.flask_bp = event_BP
        event_BP = self.flask_bp

        @event_BP.route('/daemon-event/<name>', methods=['POST'])
        def daemon_event_handler(name):
            handler: Callable

            try:
                json_data = request.get_json(force=True)
            except BadRequest:
                json_data = {}
            for handler in self.listeners:
                if handler.__name__ == name:
                    return Response(handler(**json_data))
            abort(404)

    def register_listener(self, listener: Callable):
        self.listeners.add(listener)
