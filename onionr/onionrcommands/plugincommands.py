import sys
import logger, onionrplugins as plugins

def enable_plugin(o_inst):
    if len(sys.argv) >= 3:
        plugin_name = sys.argv[2]
        logger.info('Enabling plugin "%s"...' % plugin_name)
        plugins.enable(plugin_name, o_inst)
    else:
        logger.info('%s %s <plugin>' % (sys.argv[0], sys.argv[1]))

def disable_plugin(o_inst):

    if len(sys.argv) >= 3:
        plugin_name = sys.argv[2]
        logger.info('Disabling plugin "%s"...' % plugin_name)
        plugins.disable(plugin_name, o_inst)
    else:
        logger.info('%s %s <plugin>' % (sys.argv[0], sys.argv[1]))

def reload_plugin(o_inst):
    '''
        Reloads (stops and starts) all plugins, or the given plugin
    '''

    if len(sys.argv) >= 3:
        plugin_name = sys.argv[2]
        logger.info('Reloading plugin "%s"...' % plugin_name)
        plugins.stop(plugin_name, o_inst)
        plugins.start(plugin_name, o_inst)
    else:
        logger.info('Reloading all plugins...')
        plugins.reload(o_inst)


def create_plugin(o_inst):
    '''
        Creates the directory structure for a plugin name
    '''

    if len(sys.argv) >= 3:
        try:
            plugin_name = re.sub('[^0-9a-zA-Z_]+', '', str(sys.argv[2]).lower())

            if not plugins.exists(plugin_name):
                logger.info('Creating plugin "%s"...' % plugin_name)

                os.makedirs(plugins.get_plugins_folder(plugin_name))
                with open(plugins.get_plugins_folder(plugin_name) + '/main.py', 'a') as main:
                    contents = ''
                    with open('static-data/default_plugin.py', 'rb') as file:
                        contents = file.read().decode()

                    # TODO: Fix $user. os.getlogin() is   B U G G Y
                    main.write(contents.replace('$user', 'some random developer').replace('$date', datetime.datetime.now().strftime('%Y-%m-%d')).replace('$name', plugin_name))

                with open(plugins.get_plugins_folder(plugin_name) + '/info.json', 'a') as main:
                    main.write(json.dumps({'author' : 'anonymous', 'description' : 'the default description of the plugin', 'version' : '1.0'}))

                logger.info('Enabling plugin "%s"...' % plugin_name)
                plugins.enable(plugin_name, o_inst)
            else:
                logger.warn('Cannot create plugin directory structure; plugin "%s" exists.' % plugin_name)

        except Exception as e:
            logger.error('Failed to create plugin directory structure.', e)
    else:
        logger.info('%s %s <plugin>' % (sys.argv[0], sys.argv[1]))