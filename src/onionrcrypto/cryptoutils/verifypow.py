from .. import hashers
import config, onionrproofs, logger
import onionrexceptions
def verify_POW(blockContent):
    '''
        Verifies the proof of work associated with a block
    '''
    retData = False

    dataLen = len(blockContent)

    try:
        blockContent = blockContent.encode()
    except AttributeError:
        pass

    blockHash = hashers.sha3_hash(blockContent)
    try:
        blockHash = blockHash.decode() # bytes on some versions for some reason
    except AttributeError:
        pass
    
    difficulty = onionrproofs.getDifficultyForNewBlock(blockContent)
    
    if difficulty < int(config.get('general.minimum_block_pow')):
        difficulty = int(config.get('general.minimum_block_pow'))
    mainHash = '0000000000000000000000000000000000000000000000000000000000000000'#nacl.hash.blake2b(nacl.utils.random()).decode()
    puzzle = mainHash[:difficulty]

    if blockHash[:difficulty] == puzzle:
        # logger.debug('Validated block pow')
        retData = True
    else:
        logger.debug(f"Invalid token, bad proof for {blockHash} {puzzle}")
        raise onionrexceptions.InvalidProof('Proof for %s needs to be %s' % (blockHash, puzzle))

    return retData

