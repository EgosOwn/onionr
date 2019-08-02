'''
    Onionr - Private P2P Communication

    Accept block uploads to the public API server
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
import sys
from flask import Response, abort
import blockimporter, onionrexceptions, logger
def accept_upload(request):
    resp = 'failure'
    try:
        data = request.form['block']
    except KeyError:
        logger.warn('No block specified for upload')
        pass
    else:
        if sys.getsizeof(data) < 100000000:
            try:
                if blockimporter.importBlockFromData(data):
                    resp = 'success'
                else:
                    logger.warn('Error encountered importing uploaded block')
            except onionrexceptions.BlacklistedBlock:
                logger.debug('uploaded block is blacklisted')
                pass
    if resp == 'failure':
        abort(400)
    resp = Response(resp)
    return resp