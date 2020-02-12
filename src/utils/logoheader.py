import sys, os
from . import readstatic
import logger
from etc import onionrvalues
def header(message = logger.colors.fg.pink + logger.colors.bold + 'Onionr' + logger.colors.reset + logger.colors.fg.pink + ' has started.'):
    if onionrvalues.DEVELOPMENT_MODE:
        return
    header_path = readstatic.get_static_dir() + 'header.txt'
    if os.path.exists(header_path) and logger.settings.get_level() <= logger.settings.LEVEL_INFO:
        with open(header_path, 'rb') as file:
            # only to stdout, not file or log or anything
            sys.stderr.write(file.read().decode().replace('P', logger.colors.fg.pink).replace('W', logger.colors.reset + logger.colors.bold).replace('G', logger.colors.fg.green).replace('\n', logger.colors.reset + '\n').replace('B', logger.colors.bold))

            if message:
                logger.info(logger.colors.fg.lightgreen + '-> ' + str(message) + logger.colors.reset + logger.colors.fg.lightgreen + ' <-\n', terminal=True)