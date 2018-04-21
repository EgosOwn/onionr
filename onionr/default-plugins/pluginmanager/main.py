'''
    This is the future Onionr plugin manager. TODO: Add better description.
'''

# useful libraries
import logger, config

# useful functions

def installPlugin():
    logger.info('This feature has not been created yet. Please check back later.')
    return

def uninstallPlugin():
    logger.info('This feature has not been created yet. Please check back later.')
    return

def searchPlugin():
    logger.info('This feature has not been created yet. Please check back later.')
    return

# event listeners

def on_init(api, data = None):
    global pluginapi
    pluginapi = api

    # register some commands
    api.commands.register(['install-plugin', 'installplugin', 'plugin-install', 'install', 'plugininstall'], installPlugin)
    api.commands.register(['remove-plugin', 'removeplugin', 'plugin-remove', 'uninstall-plugin', 'uninstallplugin', 'plugin-uninstall', 'uninstall', 'remove', 'pluginremove'], uninstallPlugin)
    api.commands.register(['search', 'filter-plugins', 'search-plugins', 'searchplugins', 'search-plugin', 'searchplugin', 'findplugin', 'find-plugin', 'filterplugin', 'plugin-search', 'pluginsearch'], searchPlugin)

    # add help menus once the features are actually implemented

    return
