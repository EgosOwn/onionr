'''
    Onionr - P2P Anonymous Storage Network

    This file creates http endpoints for friend management
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
import core
from flask import Blueprint, Response, request, abort

simplecache = Blueprint('simplecache', __name__)

@simplecache.route('/get/<key>')
def get_key(key):
    return

@simplecache.route('/set/<key>', methods=['POST'])
def set_key(key):
    return