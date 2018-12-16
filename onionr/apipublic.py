'''
    Onionr - P2P Anonymous Storage Network

    Handle incoming commands from other Onionr nodes, over HTTP
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
import flask, apimanager
from flask import request, Response, abort, send_from_directory
from gevent.pywsgi import WSGIServer

class APIPublic:
    def __init__(self, managerInst):
        assert isinstance(managerInst, apimanager.APIManager)
        self.app = flask.Flask(__name__) # The flask application, which recieves data from the greenlet wsgiserver
        self.httpServer = WSGIServer((managerInst.publicIP, managerInst.publicPort), self.app, log=None)

    def run(self):
        self.httpServer.serve_forever()
        return