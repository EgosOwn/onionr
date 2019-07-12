'''
    Onionr - Private P2P Communication

    This file registers blueprints for the private api server
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
import os
from httpapi import security, friendsapi, profilesapi, configapi, insertblock, miscclientapi, onionrsitesapi, apiutils
def register_private_blueprints(private_api, app):
    app.register_blueprint(security.client.ClientAPISecurity(private_api).client_api_security_bp)
    app.register_blueprint(friendsapi.friends)
    app.register_blueprint(profilesapi.profile_BP)
    app.register_blueprint(configapi.config_BP)
    app.register_blueprint(insertblock.ib)
    app.register_blueprint(miscclientapi.getblocks.client_get_blocks)
    app.register_blueprint(miscclientapi.endpoints.PrivateEndpoints(private_api).private_endpoints_bp)
    app.register_blueprint(onionrsitesapi.site_api)
    app.register_blueprint(apiutils.shutdown.shutdown_bp)
    app.register_blueprint(miscclientapi.staticfiles.static_files_bp)
    return app