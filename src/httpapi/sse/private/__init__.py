from flask import g, Blueprint
from gevent import sleep

from .. import wrapper

private_sse_blueprint = Blueprint('privatesse', __name__)
SSEWrapper = wrapper.SSEWrapper()


@private_sse_blueprint.route('/hello')
def srteam_meme():
    def print_hello():
        while True:
            yield "hello\n\n"
            sleep(1)
    return SSEWrapper.handle_sse_request(print_hello)
