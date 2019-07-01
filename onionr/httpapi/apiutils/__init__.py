import json
import core, onionrblockapi
from onionrutils import bytesconverter, stringvalidators
from . import shutdown

class GetBlockData:
    def __init__(self, client_api_inst=None):
        if client_api_inst is None:
            self.client_api_inst = None
            self.c = core.Core()
        elif isinstance(client_api_inst, core.Core):
            self.client_api_inst = None
            self.c = client_api_inst
        else:
            self.client_api_Inst = client_api_inst
            self.c = core.Core()
    
    def get_block_data(self, bHash, decrypt=False, raw=False, headerOnly=False):
        assert stringvalidators.validate_hash(bHash)
        bl = onionrblockapi.Block(bHash, core=self.c)
        if decrypt:
            bl.decrypt()
            if bl.isEncrypted and not bl.decrypted:
                raise ValueError

        if not raw:
            if not headerOnly:
                retData = {'meta':bl.bheader, 'metadata': bl.bmetadata, 'content': bl.bcontent}
                for x in list(retData.keys()):
                    try:
                        retData[x] = retData[x].decode()
                    except AttributeError:
                        pass
            else:
                validSig = False
                signer = bytesconverter.bytes_to_str(bl.signer)
                if bl.isSigned() and stringvalidators.validate_pub_key(signer) and bl.isSigner(signer):
                    validSig = True                    
                bl.bheader['validSig'] = validSig
                bl.bheader['meta'] = ''
                retData = {'meta': bl.bheader, 'metadata': bl.bmetadata}
            return json.dumps(retData)
        else:
            return bl.raw