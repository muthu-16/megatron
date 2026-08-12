import os
import json
import uuid
from typing import List, Dict, Any
from pathlib import Path

class SessionManager:
    def __init__(self):
        self.sessions_dir = Path(__file__).parent.parent / "memory" / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def new_session(self) -> str:
        """Creates a new session and returns the session ID."""
        session_id = str(uuid.uuid4())
        session_file = self.sessions_dir / f"{session_id}.json"
        
        session_data = {
            "session_id": session_id,
            "messages": [],
            "summary": ""
        }
        
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=4)
            
        return session_id

    def add_message(self, session_id: str, role: str, content: str, language: str = 'en') -> None:
        """Adds a message to the session history."""
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            return
            
        with open(session_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)
            
        session_data["messages"].append({
            "role": role,
            "content": content,
            "language": language
        })
        
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=4)

    def get_history(self, session_id: str, last_n: int = 20) -> List[Dict[str, str]]:
        """Retrieves the last N messages from the session."""
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            return []
            
        with open(session_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)
            
        messages = session_data.get("messages", [])
        return messages[-last_n:]

    def end_session(self, session_id: str, assistant: Any) -> None:
        """Ends the session, summarizes it, and stores the summary."""
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            return
            
        with open(session_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)
            
        messages = session_data.get("messages", [])
        if messages:
            # Simple list of dicts for assistant summary
            conv_for_summary = [{"role": m["role"], "content": m["content"]} for m in messages]
            # Use last message language if available
            last_lang = messages[-1].get("language", "en")
            summary = assistant.summarize_session(conv_for_summary, language=last_lang)
            session_data["summary"] = summary
            
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=4)

    def load_context(self, session_id: str) -> Dict[str, Any]:
        """Loads session messages and summary for context injection."""
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            return {"messages": [], "summary": ""}
            
        with open(session_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Returns metadata for all available sessions."""
        sessions = []
        for file in self.sessions_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data.get("session_id"),
                        "message_count": len(data.get("messages", [])),
                        "summary": data.get("summary", "")
                    })
            except Exception:
                continue
        return sessions
