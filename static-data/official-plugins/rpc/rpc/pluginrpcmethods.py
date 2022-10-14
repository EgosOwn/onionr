from jsonrpc import dispatcher

from onionrplugins.pluginapis import plugin_apis


def add_plugin_rpc_methods():
    for method in plugin_apis:
        try:
            if plugin_apis[method].json_compatible:
                dispatcher[method] = plugin_apis[method]
        except AttributeError:
            pass