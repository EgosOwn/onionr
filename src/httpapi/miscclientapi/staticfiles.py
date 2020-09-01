"""Onionr - Private P2P Communication

Register static file routes
"""
import os
import mimetypes
from flask import Blueprint, send_from_directory
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


# Was having some mime type issues on windows, this appeared to fix it.
# we have no-sniff set, so if the mime types are invalid sripts can't load.
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

static_files_bp = Blueprint('staticfiles', __name__)

# should be set to onionr install directory from onionr startup
root = os.path.dirname(os.path.realpath(__file__)) + \
    '/../../../static-data/www/'


@static_files_bp.route('/onboarding/', endpoint='onboardingIndex')
def onboard():
    return send_from_directory(f'{root}onboarding/', "index.html")


@static_files_bp.route('/onboarding/<path:path>', endpoint='onboarding')
def onboard_files(path):
    return send_from_directory(f'{root}onboarding/', path)


@static_files_bp.route('/friends/<path:path>', endpoint='friends')
def loadContacts(path):
    return send_from_directory(root + 'friends/', path)


@static_files_bp.route('/friends/', endpoint='friendsindex')
def loadContacts():
    return send_from_directory(root + 'friends/', 'index.html')


@static_files_bp.route('/profiles/<path:path>', endpoint='profiles')
def loadContacts(path):
    return send_from_directory(root + 'profiles/', path)


@static_files_bp.route('/profiles/', endpoint='profilesindex')
def loadContacts():
    return send_from_directory(root + 'profiles/', 'index.html')



@static_files_bp.route('/shared/<path:path>', endpoint='sharedContent')
def sharedContent(path):
    return send_from_directory(root + 'shared/', path)


@static_files_bp.route('/', endpoint='onionrhome')
def hello():
    # ui home
    return send_from_directory(root + 'private/', 'index.html')


@static_files_bp.route('/private/<path:path>', endpoint='homedata')
def homedata(path):
    return send_from_directory(root + 'private/', path)