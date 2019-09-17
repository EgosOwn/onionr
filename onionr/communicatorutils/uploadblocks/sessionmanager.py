"""
    Onionr - Private P2P Communication

    Manager for upload 'sessions'
"""
from __future__ import annotations
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
from typing import Iterable, Union

from onionrutils import bytesconverter

from . import session

class BlockUploadSessionManager:
    """Holds block UploadSession instances. Optionally accepts iterable of sessions to added on init

    Arguments: old_session: iterable of old UploadSession objects"""
    def __init__(self, old_sessions:Iterable=None):
        if old_sessions is None:
            self.sessions = []
        else:
            self.sessions = old_session
    
    def add_session(self, session_or_block: Union(str, bytes, session.UploadSession, Block))->session.UploadSession:
        """Create (or add existing) block upload session from a str/bytes block hex hash, existing UploadSession or Block object"""
        if isinstance(session_or_block, session.UploadSession): 
            self.sessions.append(session_or_block)
            return session_or_block
        # convert Block to hash string
        if hasattr(session_or_block, 'bheader') and hasattr(session_or_block, 'raw'): session_or_block = session_or_block.hash
        # convert bytes hash to str
        if isinstance(session_or_block, bytes): session_or_block = bytesconverter.bytes_to_str(session_or_block)
        # intentionally not elif
        if isinstance(session_or_block, str):
            new_session = session.UploadSession(session_or_block)
            self.sessions.append(new_session)
            return new_session

    def get_session(self, block_hash: Union(str, bytes))->session.UploadSession:
        block_hash = bytesconverter.bytes_to_str(block_hash).replace('=', '')
        for session in self.sessions: if session.block_hash == block_hash: return session

    def clean_session(self, specific_session: Union[str, UploadSession]):
        return