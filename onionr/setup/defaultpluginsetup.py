import os, shutil
import onionrplugins as plugins, logger
def setup_default_plugins():
    # Copy default plugins into plugins folder
    if not os.path.exists(plugins.get_plugins_folder()):
        if os.path.exists('static-data/default-plugins/'):
            names = [f for f in os.listdir("static-data/default-plugins/")]
            shutil.copytree('static-data/default-plugins/', plugins.get_plugins_folder())

            # Enable plugins
            for name in names:
                if not name in plugins.get_enabled_plugins():
                    plugins.enable(name)

    for name in plugins.get_enabled_plugins():
        if not os.path.exists(plugins.get_plugin_data_folder(name)):
            try:
                os.mkdir(plugins.get_plugin_data_folder(name))
            except Exception as e:
                #logger.warn('Error enabling plugin: ' + str(e), terminal=True)
                plugins.disable(name, stop_event = False)