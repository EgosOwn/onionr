'''
    Onionr - P2P Anonymous Storage Network

    Set default onionr http headers
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
def set_default_onionr_http_headers(flask_response):
    '''Response headers'''
    flask_response.headers['Content-Security-Policy'] = "default-src 'none'; style-src data: 'unsafe-inline'; img-src data:"
    flask_response.headers['X-Frame-Options'] = 'deny'
    flask_response.headers['X-Content-Type-Options'] = "nosniff"
    flask_response.headers['Server'] = ''
    flask_response.headers['Date'] = 'Thu, 1 Jan 1970 00:00:00 GMT' # Clock info is probably useful to attackers. Set to unix epoch.
    flask_response.headers['Connection'] = "close"
    return flask_response