import json
import logger, onionrexceptions
from etc import onionrvalues
from onionrutils import stringvalidators
def validate_metadata(utils_inst, metadata, blockData):
    '''Validate metadata meets onionr spec (does not validate proof value computation), take in either dictionary or json string'''
    # TODO, make this check sane sizes
    retData = False
    maxClockDifference = 120

    # convert to dict if it is json string
    if type(metadata) is str:
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            pass

    # Validate metadata dict for invalid keys to sizes that are too large
    maxAge = utils_inst._core.config.get("general.max_block_age", onionrvalues.OnionrValues().default_expire)
    if type(metadata) is dict:
        for i in metadata:
            try:
                utils_inst._core.requirements.blockMetadataLengths[i]
            except KeyError:
                logger.warn('Block has invalid metadata key ' + i)
                break
            else:
                testData = metadata[i]
                try:
                    testData = len(testData)
                except (TypeError, AttributeError) as e:
                    testData = len(str(testData))
                if utils_inst._core.requirements.blockMetadataLengths[i] < testData:
                    logger.warn('Block metadata key ' + i + ' exceeded maximum size')
                    break
            if i == 'time':
                if not stringvalidators.is_integer_string(metadata[i]):
                    logger.warn('Block metadata time stamp is not integer string or int')
                    break
                isFuture = (metadata[i] - utils_inst.getEpoch())
                if isFuture > maxClockDifference:
                    logger.warn('Block timestamp is skewed to the future over the max %s: %s' (maxClockDifference, isFuture))
                    break
                if (utils_inst.getEpoch() - metadata[i]) > maxAge:
                    logger.warn('Block is outdated: %s' % (metadata[i],))
                    break
            elif i == 'expire':
                try:
                    assert int(metadata[i]) > utils_inst.getEpoch()
                except AssertionError:
                    logger.warn('Block is expired: %s less than %s' % (metadata[i], utils_inst.getEpoch()))
                    break
            elif i == 'encryptType':
                try:
                    assert metadata[i] in ('asym', 'sym', '')
                except AssertionError:
                    logger.warn('Invalid encryption mode')
                    break
        else:
            # if metadata loop gets no errors, it does not break, therefore metadata is valid
            # make sure we do not have another block with the same data content (prevent data duplication and replay attacks)
            nonce = utils_inst._core._utils.bytesToStr(utils_inst._core._crypto.sha3Hash(blockData))
            try:
                with open(utils_inst._core.dataNonceFile, 'r') as nonceFile:
                    if nonce in nonceFile.read():
                        retData = False # we've seen that nonce before, so we can't pass metadata
                        raise onionrexceptions.DataExists
            except FileNotFoundError:
                retData = True
            except onionrexceptions.DataExists:
                # do not set retData to True, because nonce has been seen before
                pass
            else:
                retData = True
    else:
        logger.warn('In call to utils.validateMetadata, metadata must be JSON string or a dictionary object')

    return retData