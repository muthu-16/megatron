import sqlite3
import uuid
from typing import List, Dict, Any, Optional

class SessionStore:
    """Manages chat sessions and messages."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_session(self, user_id: str, device_id: str, language: str) -> str:
        """Creates a new session and returns its ID."""
        session_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (session_id, user_id, device_id, language)
                VALUES (?, ?, ?, ?)
            ''', (session_id, user_id, device_id, language))
            conn.commit()
        return session_id

    def add_message(self, session_id: str, role: str, content: str, language: str) -> None:
        """Adds a message to an existing session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (session_id, role, content, language)
                VALUES (?, ?, ?, ?)
            ''', (session_id, role, content, language))
            conn.commit()

    def get_messages(self, session_id: str, last_n: int = 50) -> List[Dict[str, Any]]:
        """Retrieves the last n messages for a given session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM (
                    SELECT id, session_id, role, content, language, timestamp
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ) ORDER BY timestamp ASC
            ''', (session_id, last_n))
            return [dict(row) for row in cursor.fetchall()]

    def save_summary(self, session_id: str, summary: str) -> None:
        """Saves a summary for a session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE sessions
                SET summary = ?
                WHERE session_id = ?
            ''', (summary, session_id))
            conn.commit()

    def get_last_summary(self, user_id: str) -> Optional[str]:
        """Retrieves the summary of the most recently ended or active session for a user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT summary FROM sessions
                WHERE user_id = ? AND summary IS NOT NULL
                ORDER BY started_at DESC
                LIMIT 1
            ''', (user_id,))
            row = cursor.fetchone()
            return row['summary'] if row else None

    def list_sessions(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Lists metadata of recent sessions for a user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_id, started_at, ended_at, summary, language, device_id
                FROM sessions
                WHERE user_id = ?
                ORDER BY started_at DESC
                LIMIT ?
            ''', (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def delete_session(self, session_id: str) -> None:
        """Deletes a session and all its messages."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
            conn.commit()

    def delete_all_sessions(self, user_id: str) -> None:
        """Deletes all sessions and messages for a specific user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM messages WHERE session_id IN (
                    SELECT session_id FROM sessions WHERE user_id = ?
                )
            ''', (user_id,))
            cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
            conn.commit()

    def export_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Exports all sessions and their messages for a user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM sessions WHERE user_id = ?
            ''', (user_id,))
            sessions = [dict(row) for row in cursor.fetchall()]
            
            for session in sessions:
                cursor.execute('''
                    SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC
                ''', (session['session_id'],))
                session['messages'] = [dict(row) for row in cursor.fetchall()]
                
            return sessions
