import platform
from utils import identifyhome
from etc import onionrvalues
import logger
def version(verbosity = 5, function = logger.info):
    '''
        Displays the Onionr version
    '''

    function('Onionr v%s (%s) (API v%s)' % (onionrvalues.ONIONR_VERSION, platform.machine(), onionrvalues.API_VERSION), terminal=True)
    if verbosity >= 1:
        function(onionrvalues.ONIONR_TAGLINE, terminal=True)
    if verbosity >= 2:
        function('Running on %s %s' % (platform.platform(), platform.release()), terminal=True)
        function('Onionr data dir: %s' % identifyhome.identify_home(), terminal=True)