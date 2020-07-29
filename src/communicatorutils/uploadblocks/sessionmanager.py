"""Onionr - Private P2P Communication.

Manager for upload 'sessions'
"""
from typing import List, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from deadsimplekv import DeadSimpleKV
    from session import UploadSession

from onionrutils import bytesconverter
from etc import onionrvalues
from utils import reconstructhash

from . import session
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


class BlockUploadSessionManager:
    """Holds block UploadSession instances.

    Optionally accepts iterable of sessions to added on init
    Arguments: old_session: iterable of old UploadSession objects
    """

    def __init__(self, old_sessions: List = None):
        if old_sessions is None:
            self.sessions = []
        else:
            self.sessions = old_sessions

    def add_session(self,
                    session_or_block: Union[str,
                                            bytes,
                                            session.UploadSession
                                            ]
                    ) -> session.UploadSession:
        """Create (or add existing) block upload session.

        from a str/bytes block hex hash, existing UploadSession
        """
        if isinstance(session_or_block, session.UploadSession):
            if session_or_block not in self.sessions:
                self.sessions.append(session_or_block)
            return session_or_block
        try:
            return self.get_session(session_or_block)
        except KeyError:
            pass
        # convert bytes hash to str
        if isinstance(session_or_block, bytes):
            session_or_block = bytesconverter.bytes_to_str(session_or_block)
        # intentionally not elif
        if isinstance(session_or_block, str):
            new_session = session.UploadSession(session_or_block)
            self.sessions.append(new_session)
            return new_session
        raise ValueError

    def get_session(self,
                    block_hash: Union[str, bytes]
                    ) -> session.UploadSession:
        block_hash = reconstructhash.deconstruct_hash(
            bytesconverter.bytes_to_str(block_hash))
        for sess in self.sessions:
            if sess.block_hash == block_hash:
                return sess
        raise KeyError

    def clean_session(self,
                      specific_session: Union[str, 'UploadSession'] = None):

        comm_inst: 'OnionrCommunicatorDaemon'  # type: ignore
        comm_inst = self._too_many.get_by_string(  # pylint: disable=E1101 type: ignore
        "OnionrCommunicatorDaemon")
        kv: "DeadSimpleKV" = comm_inst.shared_state.get_by_string(
            "DeadSimpleKV")
        sessions_to_delete = []
        if kv.get('startTime') < 120:
            return
        onlinePeerCount = len(kv.get('onlinePeers'))

        # If we have no online peers right now,
        if onlinePeerCount == 0:
            return

        for sess in self.sessions:
            # if over 50% of peers that were online for a session have
            # become unavailable, don't kill sessions
            if sess.total_success_count > onlinePeerCount:
                if onlinePeerCount / sess.total_success_count >= 0.5:
                    return
            # Clean sessions if they have uploaded to enough online peers
            if sess.total_success_count <= 0:
                continue
            if (sess.total_success_count / onlinePeerCount) >= \
                    onionrvalues.MIN_BLOCK_UPLOAD_PEER_PERCENT:
                sessions_to_delete.append(sess)
        for sess in sessions_to_delete:
            try:
                self.sessions.remove(session)
            except ValueError:
                pass
            # TODO cleanup to one round of search
            # Remove the blocks from the sessions, upload list,
            # and waitforshare list
            try:
                kv.get('blocksToUpload').remove(
                    reconstructhash.reconstruct_hash(sess.block_hash))
            except ValueError:
                pass
            try:
                kv.get('blocksToUpload').remove(sess.block_hash)
            except ValueError:
                pass
