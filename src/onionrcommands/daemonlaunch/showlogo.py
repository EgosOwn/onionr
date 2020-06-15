"""Onionr - Private P2P Communication.

Show nice logo
"""
import config
import logger

from .quotes import QUOTE
from utils.boxprint import bordered
from utils import logoheader

def show_logo():
    logger.raw('', terminal=True)
    # print nice header thing :)
    if config.get('general.display_header', True):
        logoheader.header("")
        if QUOTE[1]:
            logger.info(
                "\u001b[33m\033[F" + bordered(QUOTE[0] + '\n -' + QUOTE[1]),
                terminal=True)
        else:
            logger.info("\u001b[33m\033[F" + bordered(QUOTE[0]), terminal=True)