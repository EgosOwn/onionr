'''
    Onionr - Private P2P Communication

    plugin CLI commands
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

import sys
import logger, onionrplugins as plugins

def enable_plugin(o_inst):
    if len(sys.argv) >= 3:
        plugin_name = sys.argv[2]
        logger.info('Enabling plugin "%s"...' % plugin_name, terminal=True)
        plugins.enable(plugin_name, o_inst)
    else:
        logger.info('%s %s <plugin>' % (sys.argv[0], sys.argv[1]), terminal=True)

def disable_plugin(o_inst):
    if len(sys.argv) >= 3:
        plugin_name = sys.argv[2]
        logger.info('Disabling plugin "%s"...' % plugin_name, terminal=True)
        plugins.disable(plugin_name, o_inst)
    else:
        logger.info('%s %s <plugin>' % (sys.argv[0], sys.argv[1]), terminal=True)

def reload_plugin(o_inst):
    '''
        Reloads (stops and starts) all plugins, or the given plugin
    '''

    if len(sys.argv) >= 3:
        plugin_name = sys.argv[2]
        logger.info('Reloading plugin "%s"...' % plugin_name, terminal=True)
        plugins.stop(plugin_name, o_inst)
        plugins.start(plugin_name, o_inst)
    else:
        logger.info('Reloading all plugins...', terminal=True)
        plugins.reload(o_inst)


def create_plugin(o_inst):
    '''
        Creates the directory structure for a plugin name
    '''

    if len(sys.argv) >= 3:
        try:
            plugin_name = re.sub('[^0-9a-zA-Z_]+', '', str(sys.argv[2]).lower())

            if not plugins.exists(plugin_name):
                logger.info('Creating plugin "%s"...' % plugin_name, terminal=True)

                os.makedirs(plugins.get_plugins_folder(plugin_name))
                with open(plugins.get_plugins_folder(plugin_name) + '/main.py', 'a') as main:
                    contents = ''
                    with open('static-data/default_plugin.py', 'rb') as file:
                        contents = file.read().decode()

                    # TODO: Fix $user. os.getlogin() is   B U G G Y
                    main.write(contents.replace('$user', 'some random developer').replace('$date', datetime.datetime.now().strftime('%Y-%m-%d')).replace('$name', plugin_name))

                with open(plugins.get_plugins_folder(plugin_name) + '/info.json', 'a') as main:
                    main.write(json.dumps({'author' : 'anonymous', 'description' : 'the default description of the plugin', 'version' : '1.0'}))

                logger.info('Enabling plugin "%s"...' % plugin_name, terminal=True)
                plugins.enable(plugin_name, o_inst)
            else:
                logger.warn('Cannot create plugin directory structure; plugin "%s" exists.' % plugin_name, terminal=True)

        except Exception as e:
            logger.error('Failed to create plugin directory structure.', e, terminal=True)
    else:
        logger.info('%s %s <plugin>' % (sys.argv[0], sys.argv[1]), terminal=True)