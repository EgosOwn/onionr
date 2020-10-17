from os.path import exists, dirname

import ujson
from flask import Blueprint, Response, request

from utils.identifyhome import identify_home
from utils.readoffset import read_from_offset

offset_reader_api = Blueprint('offsetreaderapi', __name__)


@offset_reader_api.route('/readfileoffset/<name>')
def offset_reader_endpoint(name):
    if not name[:-4].isalnum():
        return Response(400, "Path must be alphanumeric except for file ext")

    path = identify_home() + name

    if not exists(path):
        return Response(404, "Path not found in Onionr data directory")

    offset = request.args.get('offset')

    if not offset:
        offset = 0
    else:
        offset = int(offset)
    result = read_from_offset(path, offset)._asdict()

    return ujson.dumps(result, reject_bytes=False)
