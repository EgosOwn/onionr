'''
    Onionr - Private P2P Communication

    This file primarily serves to allow specific fetching of flow board messages
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
import json
import os

from flask import Response, request, redirect, Blueprint, abort
from utils import identifyhome
import deadsimplekv as simplekv
flask_blueprint = Blueprint('flow', __name__)

with open(os.path.dirname(os.path.realpath(__file__)) + '/info.json', 'r') as info_file:
    data = info_file.read().strip()
    version = json.loads(data, strict=False)['version']

@flask_blueprint.route('/flow/getpostsbyboard/<board>')
def get_post_by_board(board):
    board_cache = simplekv.DeadSimpleKV(identifyhome.identify_home() + '/board-index.cache.json', flush_on_exit=False)
    board_cache.refresh()
    posts = board_cache.get(board)
    if posts is None:
        posts = ''
    else:
        posts = ','.join(posts)
    return Response(posts)

@flask_blueprint.route('/flow/getpostsbyboard/<board>/<offset>')
def get_post_by_board_with_offset(board, offset):
    offset = int(offset)
    OFFSET_COUNT = 10
    board_cache = simplekv.DeadSimpleKV(identifyhome.identify_home() + '/board-index.cache.json', flush_on_exit=False)
    board_cache.refresh()
    posts = board_cache.get(board)
    if posts is None:
        posts = ''
    else:
        posts.reverse()
        posts = ','.join(posts[offset:offset + OFFSET_COUNT])
    return Response(posts)

@flask_blueprint.route('/flow/version')
def get_version():
    return Response(version)
