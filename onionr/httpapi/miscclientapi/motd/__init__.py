from flask import Blueprint
from flask import Response
import unpaddedbase32

from coredb import blockmetadb
import onionrblocks
from etc import onionrvalues
import config
from onionrutils import bytesconverter

bp = Blueprint('motd', __name__)

signer = config.get("motd.motd_key", onionrvalues.MOTD_SIGN_KEY)

@bp.route('/getmotd')
def get_motd()->Response:
    motds = blockmetadb.get_blocks_by_type("motd")
    newest_time = 0
    message = "No MOTD currently present."
    for x in motds:
        bl = onionrblocks.onionrblockapi.Block(x)
        if not bl.verifySig() or bl.signer != bytesconverter.bytes_to_str(unpaddedbase32.repad(bytesconverter.str_to_bytes(signer))): continue
        if not bl.isSigner(signer): continue
        if bl.claimedTime > newest_time:
            newest_time = bl.claimedTime
            message = bl.bcontent
    return Response(message, headers={"Content-Type": "text/plain"})
