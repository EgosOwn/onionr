"""Onionr - Private P2P Communication.

Event driven interface to trigger events in communicator
"""
import json
from flask import Blueprint, request, Response
import config
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
        events: dict of current/finished events
        listeners: callables that are called when a new event is added.
            The callables name should match the event name
        _too_many: TooManyObjects instance set by external code
        """
        event_BP = Blueprint('event_BP', __name__)
        self.events = {}
        self.listeners = {}
        self.flask_bp = event_BP
        event_BP = self.flask_bp

        @event_BP.route('/daemon-event/<name>', methods=['POST'])
        def daemon_event_handler(name):
            if name in self.listeners:
                

        @event_BP.route('/daemon-event/bp-enabled')
        def bp_enabled() -> Response:
            return Response('true')

    def clean_old(self):
        """Deletes old daemon events based on their completion date."""
        pass


