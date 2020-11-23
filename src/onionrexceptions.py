"""
    Onionr - Private P2P Communication

    This file contains exceptions for onionr
"""
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

# general exceptions
class NotFound(Exception):
    pass
class Unknown(Exception):
    pass
class Invalid(Exception):
    pass

# communicator exceptions
class OnlinePeerNeeded(Exception):
    pass

# crypto exceptions
class InvalidPubkey(Exception):
    pass

class KeyNotKnown(Exception):
    pass

class DecryptionError(Exception):
    pass

class PasswordStrengthError(Exception):
    pass

class SignatureError(Exception):
    pass

# block exceptions

class PlaintextNotSupported(Exception):
    pass

class ReplayAttack(Exception):
    pass

class InvalidUpdate(Exception):
    pass

class BlockMetaEntryExists(Exception):
    pass

class InvalidMetadata(Exception):
    pass

class BlacklistedBlock(Exception):
    pass

class DataExists(Exception):
    pass

class NoDataAvailable(Exception):
    pass

class InvalidHexHash(Exception):
    """When a string is not a valid hex string of appropriate length for a hash value"""
    pass

class InvalidProof(Exception):
    """When a proof is invalid or inadequate"""
    pass

# network level exceptions
class MissingPort(Exception):
    pass

class InvalidAddress(Exception):
    pass

class InvalidAPIVersion(Exception):
    pass

class Timeout(Exception):
    pass

# file exceptions

class InsecureDirectoryUsage(IOError):
    """This occurs when a directory used by the daemon is not owned by the user.
    This is important to stop code execution attacks"""
    pass

class DiskAllocationReached(Exception):
    pass

# onionrsocket exceptions

class MissingAddress(Exception):
    pass

# Contact exceptions

class ContactDeleted(Exception):
    pass

# Version Errors

class PythonVersion(Exception):
    pass

# Auditing exceptions

class NetworkLeak(Exception):
    pass

class ArbitraryCodeExec(Exception):
    pass
