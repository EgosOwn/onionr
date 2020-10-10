"""Onionr - Private P2P Communication.

validate new block's metadata
"""
from json import JSONDecodeError
import ujson as json

import logger, onionrexceptions
from etc import onionrvalues
from . import stringvalidators, epoch, bytesconverter
import config, filepaths, onionrcrypto
"""
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
"""


def validate_metadata(metadata, block_data) -> bool:
    """Validate metadata meets onionr spec (does not validate proof value computation), take in either dictionary or json string"""

    ret_data = False
    max_clock_difference = onionrvalues.MAX_BLOCK_CLOCK_SKEW

    # convert to dict if it is json string
    if type(metadata) is str:
        try:
            metadata = json.loads(metadata)
        except JSONDecodeError:
            pass

    # Validate metadata dict for invalid keys to sizes that are too large
    maxAge = onionrvalues.DEFAULT_EXPIRE
    if type(metadata) is dict:
        for i in metadata:
            try:
                onionrvalues.BLOCK_METADATA_LENGTHS[i]
            except KeyError:
                logger.warn('Block has invalid metadata key ' + i)
                break
            else:
                testData = metadata[i]
                try:
                    testData = len(testData)
                except (TypeError, AttributeError) as e:
                    testData = len(str(testData))
                if onionrvalues.BLOCK_METADATA_LENGTHS[i] < testData:
                    logger.warn('Block metadata key ' + i + ' exceeded maximum size')
                    break
            if i == 'time':
                if not stringvalidators.is_integer_string(metadata[i]):
                    logger.warn('Block metadata time stamp is not integer string or int')
                    break
                isFuture = (metadata[i] - epoch.get_epoch())
                if isFuture > max_clock_difference:
                    logger.warn('Block timestamp is skewed to the future over the max %s: %s', (max_clock_difference, isFuture))
                    break
                if (epoch.get_epoch() - metadata[i]) > maxAge:
                    logger.warn('Block is outdated: %s' % (metadata[i],))
                    break
            elif i == 'expire':
                try:
                    if not int(metadata[i]) > epoch.get_epoch(): raise ValueError
                except ValueError:
                    logger.warn('Block is expired: %s less than %s' % (metadata[i], epoch.get_epoch()))
                    break
            elif i == 'encryptType':
                try:
                    if not metadata[i] in ('asym', 'sym', ''): raise ValueError
                except ValueError:
                    logger.warn('Invalid encryption mode')
                    break
            elif i == 'sig':
                try:
                    metadata['encryptType']
                except KeyError:
                    signer = metadata['signer']
                    sig = metadata['sig']
                    encodedMeta = bytesconverter.str_to_bytes(metadata['meta'])
                    encodedBlock = bytesconverter.str_to_bytes(block_data)
                    if not onionrcrypto.signing.ed_verify(encodedMeta + encodedBlock[1:], signer, sig):
                        logger.warn(f'Block was signed by {signer}, but signature failed')
                        break
        else:
            # if metadata loop gets no errors, it does not break, therefore metadata is valid
            # make sure we do not have another block with the same data content (prevent data duplication and replay attacks)

            # Make sure time is set (validity was checked above if it is)
            if not config.get('general.store_plaintext_blocks', True):
                try:
                    if not metadata['encryptType']:
                        raise onionrexceptions.PlaintextNotSupported
                except KeyError:
                    raise onionrexceptions.PlaintextNotSupported
            try:
                metadata['time']
            except KeyError:
                logger.warn("Time header not set")
                return False

            nonce = bytesconverter.bytes_to_str(onionrcrypto.hashers.sha3_hash(block_data))
            try:
                with open(filepaths.data_nonce_file, 'r') as nonceFile:
                    if nonce in nonceFile.read():
                        # we've seen that nonce before, so we can't pass metadata
                        raise onionrexceptions.DataExists
            except FileNotFoundError:
                ret_data = True
            except onionrexceptions.DataExists:
                # do not set ret_data to True, because data has been seen before
                logger.warn(f'{nonce} seen before')
                raise onionrexceptions.DataExists
            else:
                ret_data = True
    else:
        logger.warn('In call to utils.validateMetadata, metadata must be JSON string or a dictionary object')

    return ret_data
