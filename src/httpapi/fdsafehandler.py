from gevent.pywsgi import WSGIServer, WSGIHandler
from gevent import Timeout


class FDSafeHandler(WSGIHandler):
    '''Our WSGI handler. Doesn't do much non-default except timeouts'''
    def handle(self):
        self.timeout = Timeout(120, Exception)
        self.timeout.start()
        try:
            WSGIHandler.handle(self)
        except Timeout as ex:
            if ex is self.timeout:
                pass
            else:
                raise
