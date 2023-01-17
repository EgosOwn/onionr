"""

"""
import threading
import collections
from typing import Union

import ujson
import jsonrpc


rpc_results = collections.deque(maxlen=10000)


def get_results(id) -> Union[str, None]:
    final = None
    for result in rpc_results:
        if str(result['id']) == str(id):
            final = result
            break
    else:
        return None
    rpc_results.remove(final)
    return ujson.dumps(final)


def _exec_rpc(rpc_json_str):
    json_resp = jsonrpc.JSONRPCResponseManager.handle(
        rpc_json_str, jsonrpc.dispatcher)
    data = json_resp.data
    rpc_results.append(data)


def threaded_rpc(rpc_json_str):
    threading.Thread(
        target=_exec_rpc,
        args=(rpc_json_str,),
        daemon=True,
        name="JSON RPC").start()
