'''
    This is the future Onionr plugin manager. TODO: Add better description.
'''

# useful libraries
import logger, config
import os, sys, json

plugin_name = 'pluginmanager'

keys_data = {'keys' : {}}

# key functions

def writeKeys():
    '''
        Serializes and writes the keystore in memory to file
    '''

    file = open(keys_file, 'w')
    file.write(json.dumps(keys_data, indent=4, sort_keys=True))
    file.close()

def readKeys():
    '''
        Loads the keystore into memory
    '''

    global keys_data
    keys_data = json.loads(open(keys_file).read())
    return keys_data

def getKey(plugin):
    '''
        Returns the public key for a given plugin
    '''

    readKeys()
    return (keys_data['keys'][plugin] if plugin in keys_data['keys'] else None)

def saveKey(plugin, key):
    '''
        Saves the public key for a plugin to keystore
    '''

    keys_data['keys'][plugin] = key
    writeKeys()

def check():
    '''
        Checks to make sure the keystore file still exists
    '''

    global keys_file
    keys_file = pluginapi.plugins.get_data_folder(plugin_name) + 'keystore.json'
    if not os.path.isfile(keys_file):
        writeKeys()

# command handlers

def help():
    logger.info(sys.argv[0] + ' ' + sys.argv[1] + ' <plugin> [public key/block hash]')

def commandInstallPlugin():
    logger.warn('This feature is not functional or is still in development.')
    if len(sys.argv) >= 3:
        check()

        pluginname = sys.argv[2]
        pkobh = None # public key or block hash

        if len(sys.argv) >= 4:
            # public key or block hash specified
            pkobh = sys.argv[3]
        else:
            # none specified, check if in config file
            pkobh = getKey(pluginname)

        if pkobh is None:
            logger.error('No key for this plugin found in keystore, please specify.')
            help()
            return True

        valid_hash = pluginapi.get_utils().validateHash(pkobh)
        real_block = False
        valid_key = pluginapi.get_utils().validatePubKey(pkobh)
        real_key = False

        if valid_hash:
            real_block = pluginapi.get_utils().hasBlock(pkobh)
        elif valid_key:
            real_key = pluginapi.get_utils().hasKey(pkobh)

        blockhash = None

        if valid_hash and not real_block:
            logger.error('Block hash not found. Perhaps it has not been synced yet?')
            logger.debug('Is valid hash, but does not belong to a known block.')
            return True
        elif valid_hash and real_block:
            blockhash = str(pkobh)
            logger.debug('Using block ' + blockhash + '...')
        elif valid_key and not real_key:
            logger.error('Public key not found. Try adding the node by address manually, if possible.')
            logger.debug('Is valid key, but the key is not a known one.')
        elif valid_key and real_key:
            publickey = str(pkobh)
            logger.debug('Using public key ' + publickey + '...')

            saveKey(pluginname, pkobh)
        else:
            logger.error('Unknown data \"' + str(pkobh) + '\"; must be public key or block hash.')
            return
    else:
        help()

    return True

def commandUninstallPlugin():
    logger.info('This feature has not been created yet. Please check back later.')
    return

def commandSearchPlugin():
    logger.info('This feature has not been created yet. Please check back later.')
    return

# event listeners

def on_init(api, data = None):
    global pluginapi
    pluginapi = api
    check()

    # register some commands
    api.commands.register(['install-plugin', 'installplugin', 'plugin-install', 'install', 'plugininstall'], commandInstallPlugin)
    api.commands.register(['remove-plugin', 'removeplugin', 'plugin-remove', 'uninstall-plugin', 'uninstallplugin', 'plugin-uninstall', 'uninstall', 'remove', 'pluginremove'], commandUninstallPlugin)
    api.commands.register(['search', 'filter-plugins', 'search-plugins', 'searchplugins', 'search-plugin', 'searchplugin', 'findplugin', 'find-plugin', 'filterplugin', 'plugin-search', 'pluginsearch'], commandSearchPlugin)

    # add help menus once the features are actually implemented

    return
