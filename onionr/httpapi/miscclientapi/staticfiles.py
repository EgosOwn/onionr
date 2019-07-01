'''
    Onionr - Private P2P Communication

    Register static file routes
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
from flask import Blueprint, send_from_directory

static_files_bp = Blueprint('staticfiles', __name__)

@static_files_bp.route('/board/', endpoint='board')
def loadBoard():
    return send_from_directory('static-data/www/board/', "index.html")

@static_files_bp.route('/mail/<path:path>', endpoint='mail')
def loadMail(path):
    return send_from_directory('static-data/www/mail/', path)

@static_files_bp.route('/mail/', endpoint='mailindex')
def loadMailIndex():
    return send_from_directory('static-data/www/mail/', 'index.html')

@static_files_bp.route('/clandestine/<path:path>', endpoint='clandestine')
def loadClandestine(path):
    return send_from_directory('static-data/www/clandestine/', path)

@static_files_bp.route('/clandestine/', endpoint='clandestineIndex')
def loadClandestineIndex():
    return send_from_directory('static-data/www/clandestine/', 'index.html')

@static_files_bp.route('/friends/<path:path>', endpoint='friends')
def loadContacts(path):
    return send_from_directory('static-data/www/friends/', path)

@static_files_bp.route('/friends/', endpoint='friendsindex')
def loadContacts():
    return send_from_directory('static-data/www/friends/', 'index.html')

@static_files_bp.route('/profiles/<path:path>', endpoint='profiles')
def loadContacts(path):
    return send_from_directory('static-data/www/profiles/', path)

@static_files_bp.route('/profiles/', endpoint='profilesindex')
def loadContacts():
    return send_from_directory('static-data/www/profiles/', 'index.html')

@static_files_bp.route('/board/<path:path>', endpoint='boardContent')
def boardContent(path):
    return send_from_directory('static-data/www/board/', path)

@static_files_bp.route('/shared/<path:path>', endpoint='sharedContent')
def sharedContent(path):
    return send_from_directory('static-data/www/shared/', path)

@static_files_bp.route('/', endpoint='onionrhome')
def hello():
    # ui home
    return send_from_directory('static-data/www/private/', 'index.html')

@static_files_bp.route('/private/<path:path>', endpoint='homedata')
def homedata(path):
    return send_from_directory('static-data/www/private/', path)