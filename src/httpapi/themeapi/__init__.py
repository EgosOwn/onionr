"""
    Onionr - Private P2P Communication

    API to get current CSS theme for the client web UI
"""
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
from flask import Blueprint, Response

import config
from utils import readstatic

theme_blueprint = Blueprint('themes', __name__)

LIGHT_THEME_FILES = ['bulma-light.min.css', 'styles-light.css']
DARK_THEME_FILES = ['bulma-dark.min.css', 'styles-dark.css']

def _load_from_files(file_list: list)->str:
    """Loads multiple static dir files and returns them in combined string format (non-binary)"""
    combo_data = ''
    for f in file_list:
        combo_data += readstatic.read_static('www/shared/main/themes/' + f)
    return combo_data

@theme_blueprint.route('/gettheme', endpoint='getTheme')
def get_theme_file()->Response:
    """Returns the css theme data"""
    css: str
    theme = config.get('ui.theme', 'dark').lower()
    if theme == 'dark':
        css = _load_from_files(DARK_THEME_FILES)
    elif theme == 'light':
        css = _load_from_files(LIGHT_THEME_FILES)
    return Response(css, mimetype='text/css')
