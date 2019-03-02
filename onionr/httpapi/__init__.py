from flask import request
import onionrplugins

def load_plugin_blueprints(flaskapp):
    for plugin in onionrplugins.get_enabled_plugins():
        plugin = onionrplugins.get_plugin(plugin)
        try:
            flaskapp.register_blueprint(getattr(plugin, 'flask_blueprint'))
        except AttributeError:
            pass