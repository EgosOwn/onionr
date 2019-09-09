'''
    Onionr - Private P2P Communication

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
FEATURE_POLICY = """vibrate; vr; webauthn; usb; sync-xhr; speaker; 
picture-in-picture; payment; midi; microphone; magnetometer; gyroscope; 
geolocation; fullscreen; encrypted-media; document-domain; 
camera; accelerometer; ambient-light-sensor""".replace('\n', '') # have to remove \n for flask
def set_default_onionr_http_headers(flask_response):
    '''Response headers'''
    flask_response.headers['Content-Security-Policy'] = "default-src 'none'; style-src data: 'unsafe-inline'; img-src data:"
    flask_response.headers['X-Frame-Options'] = 'deny'
    flask_response.headers['X-Content-Type-Options'] = "nosniff"
    flask_response.headers['Server'] = ''
    flask_response.headers['Date'] = 'Thu, 1 Jan 1970 00:00:00 GMT' # Clock info is probably useful to attackers. Set to unix epoch.
    flask_response.headers['Connection'] = "close"
    flask_response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage", "executionContexts"'
    flask_response.headers['Feature-Policy'] = FEATURE_POLICY
    flask_response.headers['Referrer-Policy'] = 'same-origin'
    return flask_response