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
        pf = platform.platform()
        release = platform.release()
        python_imp = platform.python_implementation()
        python_version = platform.python_version()
        function(f'{python_imp} {python_version} on {pf} {release}', terminal=True)
        function('Onionr data dir: %s' % identifyhome.identify_home(), terminal=True)

version.onionr_help = 'Shows environment details including Onionr version & data directory, OS and Python version'
