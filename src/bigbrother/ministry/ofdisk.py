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
        if 'proc' in info[0]:
            logger.warn(f'[DISK MINISTRY] {info} - probably built in Onionr stats')
        else:
            logger.warn(f'[DISK MINISTRY] {info}')
