"""Onionr - Private P2P Communication.

This file primarily serves to allow specific fetching of circles board messages
"""
import operator
import os

import ujson as json

from flask import Response, Blueprint
from flask import send_from_directory
from deadsimplekv import DeadSimpleKV

from utils import identifyhome
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

flask_blueprint = Blueprint('circles', __name__)

root = os.path.dirname(os.path.realpath(__file__))


with open(
    os.path.dirname(
        os.path.realpath(__file__)) + '/info.json', 'r') as info_file:
    data = info_file.read().strip()
    version = json.loads(data)['version']

BOARD_CACHE_FILE = identifyhome.identify_home() + '/board-index.cache.json'

read_only_cache = DeadSimpleKV(
    BOARD_CACHE_FILE,
    flush_on_exit=False,
    refresh_seconds=30)

@flask_blueprint.route('/board/<path:path>', endpoint='circlesstatic')
def load_mail(path):
    return send_from_directory(root + '/web/', path)


@flask_blueprint.route('/board/', endpoint='circlesindex')
def load_mail_index():
    return send_from_directory(root + '/web/', 'index.html')


@flask_blueprint.route('/circles/getpostsbyboard/<board>')
def get_post_by_board(board):
    board_cache = DeadSimpleKV(
        BOARD_CACHE_FILE,
        flush_on_exit=False)
    board_cache.refresh()
    posts = board_cache.get(board)
    if posts is None:
        posts = ''
    else:
        posts = ','.join(posts)
    return Response(posts)


@flask_blueprint.route('/circles/getpostsbyboard/<board>/<offset>')
def get_post_by_board_with_offset(board, offset):
    offset = int(offset)
    OFFSET_COUNT = 10
    board_cache = DeadSimpleKV(
        BOARD_CACHE_FILE,
        flush_on_exit=False)
    board_cache.refresh()
    posts = board_cache.get(board)
    if posts is None:
        posts = ''
    else:
        posts.reverse()
        posts = ','.join(posts[offset:offset + OFFSET_COUNT])
    return Response(posts)


@flask_blueprint.route('/circles/version')
def get_version():
    return Response(version)


@flask_blueprint.route('/circles/removefromcache/<board>/<name>',
                       methods=['POST'])
def remove_from_cache(board, name):
    board_cache = DeadSimpleKV(BOARD_CACHE_FILE,
                               flush_on_exit=False)
    board_cache.refresh()
    posts = board_cache.get(board)
    try:
        posts.remove(name)
    except ValueError:
        pass
    board_cache.put(board, posts)
    return Response('success')


@flask_blueprint.route('/circles/getpopular/<count>')
def get_popular(count):
    read_only_cache.refresh()
    boards = json.loads(read_only_cache.get_raw_json())
    for board in boards:
        boards[board] = len(boards[board])


    top_boards = sorted(boards.items(), key=operator.itemgetter(1), reverse=True)[:int(count)]

    only_board_names = []
    for b in top_boards:
        only_board_names.append(b[0])

    return Response(','.join(only_board_names), content_type='text/csv')
