'''
    Onionr - Private P2P Communication

    validate new block's metadata
'''
'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import json
import logger, onionrexceptions
from etc import onionrvalues
from onionrutils import stringvalidators, epoch, bytesconverter
import config, onionrvalues, filepaths, onionrcrypto
def validate_metadata(metadata, blockData):
    '''Validate metadata meets onionr spec (does not validate proof value computation), take in either dictionary or json string'''
    # TODO, make this check sane sizes
    crypto = onionrcrypto.OnionrCrypto()
    requirements = onionrvalues.OnionrValues()
    retData = False
    maxClockDifference = 120

    # convert to dict if it is json string
    if type(metadata) is str:
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            pass

    # Validate metadata dict for invalid keys to sizes that are too large
    maxAge = config.get("general.max_block_age", onionrvalues.OnionrValues().default_expire)
    if type(metadata) is dict:
        for i in metadata:
            try:
                requirements.blockMetadataLengths[i]
            except KeyError:
                logger.warn('Block has invalid metadata key ' + i)
                break
            else:
                testData = metadata[i]
                try:
                    testData = len(testData)
                except (TypeError, AttributeError) as e:
                    testData = len(str(testData))
                if requirements.blockMetadataLengths[i] < testData:
                    logger.warn('Block metadata key ' + i + ' exceeded maximum size')
                    break
            if i == 'time':
                if not stringvalidators.is_integer_string(metadata[i]):
                    logger.warn('Block metadata time stamp is not integer string or int')
                    break
                isFuture = (metadata[i] - epoch.get_epoch())
                if isFuture > maxClockDifference:
                    logger.warn('Block timestamp is skewed to the future over the max %s: %s' (maxClockDifference, isFuture))
                    break
                if (epoch.get_epoch() - metadata[i]) > maxAge:
                    logger.warn('Block is outdated: %s' % (metadata[i],))
                    break
            elif i == 'expire':
                try:
                    assert int(metadata[i]) > epoch.get_epoch()
                except AssertionError:
                    logger.warn('Block is expired: %s less than %s' % (metadata[i], epoch.get_epoch()))
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
            nonce = bytesconverter.bytes_to_str(crypto.sha3Hash(blockData))
            try:
                with open(filepaths.data_nonce_file, 'r') as nonceFile:
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