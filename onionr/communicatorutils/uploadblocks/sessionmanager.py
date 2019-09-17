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
class BlockUploadSessionManager:
    def __init__(self, old_sessions:Iterable=None):
        if old_session is None:
            self.sessions = []
        else:
            self.sessions = old_session
    
    def add_session(self, session_or_block: Union(str, bytes, UploadSession, Block)):
        """Create (or add existing) block upload session from a str/bytes block hex hash, existing UploadSession or Block object"""
        if isinstance(session_or_block, bytes): session_or_block = bytesconverter.bytes_to_str(session_or_block)
        if isinstance(session_or_block, str):
            self.sessions.append()

    def clean_session(self, specific_session: Union[str, UploadSession]):
        return