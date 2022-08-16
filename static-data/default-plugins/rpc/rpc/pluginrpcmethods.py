from jsonrpc import dispatcher

from onionrplugins.pluginapis import plugin_apis


def add_plugin_rpc_methods():
    for method in plugin_apis:
        dispatcher[method] = plugin_apis[method]