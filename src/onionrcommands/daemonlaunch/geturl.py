"""Onionr - Private P2P Communication.

Open the web interface properly into a web browser, and return it
"""
import logger
from onionrutils import getclientapiserver


def get_url(config) -> str:
    """Build UI URL string and return it."""
    onboarding = ""
    if not config.get('onboarding.done', False):
        onboarding = "onboarding/"
    try:
        url = getclientapiserver.get_client_API_server()
    except FileNotFoundError:
        url = ""
        logger.error(
            'Onionr seems to not be running (could not get api host)',
            terminal=True)
    else:
        url = 'http://%s/%s#%s' % (url, onboarding, config.get('client.webpassword'))
        logger.info('Onionr web interface URL: ' + url, terminal=True)
    return url
