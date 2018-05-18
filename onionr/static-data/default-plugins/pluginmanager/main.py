'''
    Onionr - P2P Microblogging Platform & Social network.

    This plugin acts as a plugin manager, and allows the user to install other plugins distributed over Onionr.
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

# useful libraries
import logger, config
import os, sys, json, time, random, shutil, base64, getpass, datetime, re
from onionrblockapi import Block

plugin_name = 'pluginmanager'

keys_data = {'keys' : {}, 'plugins' : [], 'repositories' : {}}

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

    global keys_data
    readKeys()
    return (keys_data['keys'][plugin] if plugin in keys_data['keys'] else None)

def saveKey(plugin, key):
    '''
        Saves the public key for a plugin to keystore
    '''

    global keys_data
    readKeys()
    keys_data['keys'][plugin] = key
    writeKeys()

def getPlugins():
    '''
        Returns a list of plugins installed by the plugin manager
    '''

    global keys_data
    readKeys()
    return keys_data['plugins']

def addPlugin(plugin):
    '''
        Saves the plugin name, to remember that it was installed by the pluginmanager
    '''

    global keys_data
    readKeys()
    if not plugin in keys_data['plugins']:
        keys_data['plugins'].append(plugin)
        writeKeys()

def removePlugin(plugin):
    '''
        Removes the plugin name from the pluginmanager's records
    '''

    global keys_data
    readKeys()
    if plugin in keys_data['plugins']:
        keys_data['plugins'].remove(plugin)
        writeKeys()

def getRepositories():
    '''
        Returns a list of plugins installed by the plugin manager
    '''

    global keys_data
    readKeys()
    return keys_data['repositories']

def addRepository(repositories, data):
    '''
        Saves the plugin name, to remember that it was installed by the pluginmanager
    '''

    global keys_data
    readKeys()
    keys_data['repositories'][repositories] = data
    writeKeys()

def removeRepository(repositories):
    '''
        Removes the plugin name from the pluginmanager's records
    '''

    global keys_data
    readKeys()
    if plugin in keys_data['repositories']:
        del keys_data['repositories'][repositories]
        writeKeys()

def check():
    '''
        Checks to make sure the keystore file still exists
    '''

    global keys_file
    keys_file = pluginapi.plugins.get_data_folder(plugin_name) + 'keystore.json'
    if not os.path.isfile(keys_file):
        writeKeys()

# plugin management

def sanitize(name):
    return re.sub('[^0-9a-zA-Z]+', '', str(name).lower())[:255]

def blockToPlugin(block):
    try:
        block = Block(block)
        blockContent = json.loads(block.getContent())

        name = sanitize(blockContent['name'])
        author = blockContent['author']
        date = blockContent['date']
        version = None

        if 'version' in blockContent['info']:
            version = blockContent['info']['version']

        content = base64.b64decode(blockContent['content'].encode())

        source = pluginapi.plugins.get_data_folder(plugin_name) + 'plugin.zip'
        destination = pluginapi.plugins.get_folder(name)

        with open(source, 'wb') as f:
            f.write(content)

        if os.path.exists(destination) and not os.path.isfile(destination):
            shutil.rmtree(destination)

        shutil.unpack_archive(source, destination)
        pluginapi.plugins.enable(name)

        logger.info('Installation of %s complete.' % name)

        return True
    except Exception as e:
        logger.error('Failed to install plugin.', error = e, timestamp = False)

    return False

def pluginToBlock(plugin, import_block = True):
    try:
        plugin = sanitize(plugin)

        directory = pluginapi.get_pluginapi().get_folder(plugin)
        data_directory = pluginapi.get_pluginapi().get_data_folder(plugin)
        zipfile = pluginapi.get_pluginapi().get_data_folder(plugin_name) + 'plugin.zip'

        if os.path.exists(directory) and not os.path.isfile(directory):
            if os.path.exists(data_directory) and not os.path.isfile(data_directory):
                shutil.rmtree(data_directory)
            if os.path.exists(zipfile) and os.path.isfile(zipfile):
                os.remove(zipfile)
            if os.path.exists(directory + '__pycache__') and not os.path.isfile(directory + '__pycache__'):
                shutil.rmtree(directory + '__pycache__')

            shutil.make_archive(zipfile[:-4], 'zip', directory)
            data = base64.b64encode(open(zipfile, 'rb').read())

            author = getpass.getuser()
            description = 'Default plugin description'
            info = {"name" : plugin}
            try:
                if os.path.exists(directory + 'info.json'):
                    info = json.loads(open(directory + 'info.json').read())
                    if 'author' in info:
                        author = info['author']
                    if 'description' in info:
                        description = info['description']
            except:
                pass

            metadata = {'author' : author, 'date' : str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'name' : plugin, 'info' : info, 'compiled-by' : plugin_name, 'content' : data.decode('utf-8'), 'description' : description}

            hash = pluginapi.get_core().insertBlock(json.dumps(metadata), header = 'plugin', sign = True)

            if import_block:
                pluginapi.get_utils().importNewBlocks()

            return hash
        else:
            logger.error('Plugin %s does not exist.' % plugin)
    except Exception as e:
        logger.error('Failed to convert plugin to block.', error = e, timestamp = False)

    return False

def installBlock(block):
    try:
        block = Block(block)
        blockContent = json.loads(block.getContent())

        name = sanitize(blockContent['name'])
        author = blockContent['author']
        date = blockContent['date']
        version = None

        if 'version' in blockContent['info']:
            version = blockContent['info']['version']

        install = False

        logger.info(('Will install %s' + (' v' + version if not version is None else '') + ' (%s), by %s') % (name, date, author))

        # TODO: Convert to single line if statement
        if os.path.exists(pluginapi.plugins.get_folder(name)):
            install = logger.confirm(message = 'Continue with installation (will overwrite existing plugin) %s?')
        else:
            install = logger.confirm(message = 'Continue with installation %s?')

        if install:
            blockToPlugin(block.getHash())
            addPlugin(name)
        else:
            logger.info('Installation cancelled.')
            return False

        return True
    except Exception as e:
        logger.error('Failed to install plugin.', error = e, timestamp = False)
        return False

def uninstallPlugin(plugin):
    try:
        plugin = sanitize(plugin)

        pluginFolder = pluginapi.plugins.get_folder(plugin)
        exists = (os.path.exists(pluginFolder) and not os.path.isfile(pluginFolder))
        installedByPluginManager = plugin in getPlugins()
        remove = False

        if not exists:
            logger.warn('Plugin %s does not exist.' % plugin, timestamp = False)
            return False

        default = 'y'
        if not installedByPluginManager:
            logger.warn('The plugin %s was not installed by %s.' % (plugin, plugin_name), timestamp = False)
            default = 'n'
        remove = logger.confirm(message = 'All plugin data will be lost. Are you sure you want to proceed %s?', default = default)

        if remove:
            if installedByPluginManager:
                removePlugin(plugin)
            pluginapi.plugins.disable(plugin)
            shutil.rmtree(pluginFolder)

            logger.info('Uninstallation of %s complete.' % plugin)

            return True
        else:
            logger.info('Uninstallation cancelled.')
    except Exception as e:
        logger.error('Failed to uninstall plugin.', error = e)
    return False

# command handlers

def help():
    logger.info(sys.argv[0] + ' ' + sys.argv[1] + ' <plugin> [public key/block hash]')
    logger.info(sys.argv[0] + ' ' + sys.argv[1] + ' <plugin> [public key/block hash]')

def commandInstallPlugin():
    if len(sys.argv) >= 3:
        check()

        pluginname = sys.argv[2]
        pkobh = None # public key or block hash

        version = None
        if ':' in pluginname:
            details = pluginname
            pluginname = sanitize(details[0])
            version = details[1]

        sanitize(pluginname)

        if len(sys.argv) >= 4:
            # public key or block hash specified
            pkobh = sys.argv[3]
        else:
            # none specified, check if in config file
            pkobh = getKey(pluginname)

        if pkobh is None:
            # still nothing found, try searching repositories
            logger.info('Searching for public key in repositories...')
            try:
                repos = getRepositories()
                distributors = list()
                for repo, records in repos.items():
                    if pluginname in records:
                        logger.debug('Found %s in repository %s for plugin %s.' % (records[pluginname], repo, pluginname))
                        distributors.append(records[pluginname])

                if len(distributors) != 0:
                    distributor = None

                    if len(distributors) == 1:
                        logger.info('Found distributor: %s' % distributors[0])
                        distributor = distributors[0]
                    else:
                        distributors_message = ''

                        index = 1
                        for dist in distributors:
                            distributors_message += '    ' + logger.colors.bold + str(index) + ') ' + logger.colors.reset + str(dist) + '\n'
                            index += 1

                        logger.info((logger.colors.bold + 'Found distributors (%s):' + logger.colors.reset + '\n' + distributors_message) % len(distributors))

                        valid = False
                        while not valid:
                            choice = logger.readline('Select the number of the key to use, from 1 to %s, or press Ctrl+C to cancel:' % (index - 1))

                            try:
                                if int(choice) < index and int(choice) >= 1:
                                    distributor = distributors[int(choice)]
                                    valid = True
                            except KeyboardInterrupt:
                                logger.info('Installation cancelled.')
                                return True
                            except:
                                pass

                    if not distributor is None:
                        pkobh = distributor
            except Exception as e:
                logger.warn('Failed to lookup plugin in repositories.', timestamp = False)
                logger.error('asdf', error = e, timestamp = False)

        if pkobh is None:
            logger.error('No key for this plugin found in keystore or repositories, please specify.')
            help()
            return True

        valid_hash = pluginapi.get_utils().validateHash(pkobh)
        real_block = False
        valid_key = pluginapi.get_utils().validatePubKey(pkobh)
        real_key = False

        if valid_hash:
            real_block = Block.exists(pkobh)
        elif valid_key:
            real_key = pluginapi.get_utils().hasKey(pkobh)

        blockhash = None

        if valid_hash and not real_block:
            logger.error('Block hash not found. Perhaps it has not been synced yet?')
            logger.debug('Is valid hash, but does not belong to a known block.')

            return True
        elif valid_hash and real_block:
            blockhash = str(pkobh)
            logger.debug('Using block %s...' % blockhash)

            installBlock(blockhash)
        elif valid_key and not real_key:
            logger.error('Public key not found. Try adding the node by address manually, if possible.')
            logger.debug('Is valid key, but the key is not a known one.')
        elif valid_key and real_key:
            publickey = str(pkobh)
            logger.debug('Using public key %s...' % publickey)

            saveKey(pluginname, pkobh)

            signedBlocks = Block.getBlocks(type = 'plugin', signed = True, signer = publickey)

            mostRecentTimestamp = None
            mostRecentVersionBlock = None

            for block in signedBlocks:
                try:
                    blockContent = json.loads(block.getContent())

                    if not (('author' in blockContent) and ('info' in blockContent) and ('date' in blockContent) and ('name' in blockContent)):
                        raise ValueError('Missing required parameter `date` in block %s.' % block.getHash())

                    blockDatetime = datetime.datetime.strptime(blockContent['date'], '%Y-%m-%d %H:%M:%S')

                    if blockContent['name'] == pluginname:
                        if ('version' in blockContent['info']) and (blockContent['info']['version'] == version) and (not version is None):
                            mostRecentTimestamp = blockDatetime
                            mostRecentVersionBlock = block.getHash()
                            break
                        elif mostRecentTimestamp is None:
                            mostRecentTimestamp = blockDatetime
                            mostRecentVersionBlock = block.getHash()
                        elif blockDatetime > mostRecentTimestamp:
                            mostRecentTimestamp = blockDatetime
                            mostRecentVersionBlock = block.getHash()
                except Exception as e:
                    pass

            logger.warn('Only continue the installation is you are absolutely certain that you trust the plugin distributor. Public key of plugin distributor: %s' % publickey, timestamp = False)
            installBlock(mostRecentVersionBlock)
        else:
            logger.error('Unknown data "%s"; must be public key or block hash.' % str(pkobh))
            return
    else:
        logger.info(sys.argv[0] + ' ' + sys.argv[1] + ' <plugin> [public key/block hash]')

    return True

def commandUninstallPlugin():
    if len(sys.argv) >= 3:
        uninstallPlugin(sys.argv[2])
    else:
        logger.info(sys.argv[0] + ' ' + sys.argv[1] + ' <plugin>')

    return True

def commandSearchPlugin():
    logger.info('This feature has not been created yet. Please check back later.')
    return True

def commandAddRepository():
    if len(sys.argv) >= 3:
        check()

        blockhash = sys.argv[2]

        if pluginapi.get_utils().validateHash(blockhash):
            if Block.exists(blockhash):
                try:
                    blockContent = json.loads(Block(blockhash).getContent())

                    pluginslist = dict()

                    for pluginname, distributor in blockContent['plugins'].items():
                        if pluginapi.get_utils().validatePubKey(distributor):
                            pluginslist[pluginname] = distributor

                    logger.debug('Found %s records in repository.' % len(pluginslist))

                    if len(pluginslist) != 0:
                        addRepository(blockhash, pluginslist)
                        logger.info('Successfully added repository.')
                    else:
                        logger.error('Repository contains no records, not importing.')
                except Exception as e:
                    logger.error('Failed to parse block.', error = e)
            else:
                logger.error('Block hash not found. Perhaps it has not been synced yet?')
                logger.debug('Is valid hash, but does not belong to a known block.')
        else:
            logger.error('Unknown data "%s"; must be block hash.' % str(pkobh))
    else:
        logger.info(sys.argv[0] + ' ' + sys.argv[1] + ' [block hash]')

    return True

def commandRemoveRepository():
    if len(sys.argv) >= 3:
        check()

        blockhash = sys.argv[2]

        if pluginapi.get_utils().validateHash(blockhash):
            if blockhash in getRepositories():
                try:
                    removeRepository(blockhash)
                except Exception as e:
                    logger.error('Failed to parse block.', error = e)
            else:
                logger.error('Repository has not been imported, nothing to remove.')
        else:
            logger.error('Unknown data "%s"; must be block hash.' % str(pkobh))
    else:
        logger.info(sys.argv[0] + ' ' + sys.argv[1] + ' [block hash]')

    return True

def commandPublishPlugin():
    if len(sys.argv) >= 3:
        check()

        pluginname = sanitize(sys.argv[2])
        pluginfolder = pluginapi.plugins.get_folder(pluginname)

        if os.path.exists(pluginfolder) and not os.path.isfile(pluginfolder):
            block = pluginToBlock(pluginname)
            logger.info('Plugin saved in block %s.' % block)
        else:
            logger.error('Plugin %s does not exist.' % pluginname, timestamp = False)
    else:
        logger.info(sys.argv[0] + ' ' + sys.argv[1] + ' <plugin>')

# event listeners

def on_init(api, data = None):
    global pluginapi
    pluginapi = api
    check()

    # register some commands
    api.commands.register(['install-plugin', 'installplugin', 'plugin-install', 'install', 'plugininstall'], commandInstallPlugin)
    api.commands.register(['remove-plugin', 'removeplugin', 'plugin-remove', 'uninstall-plugin', 'uninstallplugin', 'plugin-uninstall', 'uninstall', 'remove', 'pluginremove'], commandUninstallPlugin)
    api.commands.register(['search', 'filter-plugins', 'search-plugins', 'searchplugins', 'search-plugin', 'searchplugin', 'findplugin', 'find-plugin', 'filterplugin', 'plugin-search', 'pluginsearch'], commandSearchPlugin)
    api.commands.register(['add-repo', 'add-repository', 'addrepo', 'addrepository', 'repository-add', 'repo-add', 'repoadd', 'addrepository', 'add-plugin-repository', 'add-plugin-repo', 'add-pluginrepo', 'add-pluginrepository', 'addpluginrepo', 'addpluginrepository'], commandAddRepository)
    api.commands.register(['remove-repo', 'remove-repository', 'removerepo', 'removerepository', 'repository-remove', 'repo-remove', 'reporemove', 'removerepository', 'remove-plugin-repository', 'remove-plugin-repo', 'remove-pluginrepo', 'remove-pluginrepository', 'removepluginrepo', 'removepluginrepository', 'rm-repo', 'rm-repository', 'rmrepo', 'rmrepository', 'repository-rm', 'repo-rm', 'reporm', 'rmrepository', 'rm-plugin-repository', 'rm-plugin-repo', 'rm-pluginrepo', 'rm-pluginrepository', 'rmpluginrepo', 'rmpluginrepository'], commandRemoveRepository)
    api.commands.register(['publish-plugin', 'plugin-publish', 'publishplugin', 'pluginpublish', 'publish'], commandPublishPlugin)

    # add help menus once the features are actually implemented

    return
