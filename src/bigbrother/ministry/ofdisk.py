from utils.identifyhome import identify_home
import logger


def detect_disk_access(info):
    if type(info[0]) is int: return

    if '/dev/null' == info[0]: return

    whitelist = [identify_home(), 'onionr/src/', '/site-packages/', '/usr/lib64/']

    for item in whitelist:
        if item in info[0]:
            return

    if identify_home() not in info[0]:
        if 'proc' not in info[0]:  # if it is, it is onionr stats
            logger.warn(f'[DISK MINISTRY] {info}')
