import onionrplugins
def load_plugin_security_whitelist_endpoints(whitelist: list):
    """Accept a list reference of whitelist endpoints from security/client.py and
    append plugin's specified endpoints to them by attribute"""
    for plugin in onionrplugins.get_enabled_plugins():
        try:
            plugin = onionrplugins.get_plugin(plugin)
        except FileNotFoundError:
            continue
        try:
            whitelist.extend(getattr(plugin, "security_whitelist"))
        except AttributeError:
            pass