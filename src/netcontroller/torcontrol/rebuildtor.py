import time
from coredb import daemonqueue

def rebuild():
    daemonqueue.daemon_queue_add('restartTor')
