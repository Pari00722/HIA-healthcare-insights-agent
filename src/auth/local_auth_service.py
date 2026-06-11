from datetime import datetime
import uuid

import streamlit as st


class LocalAuthService:
    """In-memory auth/session service for local demo mode."""

    DEMO_USER_ID = "demo-user"

    def __init__(self):
        self._init_state()
        self.ensure_demo_session()

    def _init_state(self):
        if "local_users" not in st.session_state:
            st.session_state.local_users = {
                self.DEMO_USER_ID: {
                    "id": self.DEMO_USER_ID,
                    "email": "demo@local",
                    "name": "Demo User",
                    "created_at": datetime.now().isoformat(),
                }
            }
        if "local_chat_sessions" not in st.session_state:
            st.session_state.local_chat_sessions = {}
        if "local_chat_messages" not in st.session_state:
            st.session_state.local_chat_messages = {}

    def ensure_demo_session(self):
        user_data = st.session_state.local_users[self.DEMO_USER_ID]
        st.session_state.user = user_data
        st.session_state.auth_token = "demo-token"
        st.session_state.refresh_token = "demo-refresh-token"
        return user_data

    def try_restore_session(self):
        return self.ensure_demo_session()

    def validate_email(self, email):
        return bool(email and "@" in email)

    def check_existing_user(self, email):
        return any(user["email"] == email for user in st.session_state.local_users.values())

    def sign_up(self, email, password, name):
        if not email or not name:
            return False, "Please provide a name and email."

        if self.check_existing_user(email):
            return False, "Email already registered in demo mode."

        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "email": email,
            "name": name,
            "created_at": datetime.now().isoformat(),
        }
        st.session_state.local_users[user_id] = user_data
        st.session_state.user = user_data
        st.session_state.auth_token = f"demo-token-{user_id}"
        st.session_state.refresh_token = f"demo-refresh-{user_id}"
        return True, user_data

    def sign_in(self, email, password):
        for user in st.session_state.local_users.values():
            if user["email"] == email:
                st.session_state.user = user
                st.session_state.auth_token = f"demo-token-{user['id']}"
                st.session_state.refresh_token = f"demo-refresh-{user['id']}"
                return True, user

        return False, "User not found in demo mode. Use Sign Up to create a local demo account."

    def sign_out(self):
        # Reset demo data for a clean local session.
        for key in ("local_chat_sessions", "local_chat_messages", "current_session", "current_report_text"):
            if key in st.session_state:
                del st.session_state[key]

        self._init_state()
        self.ensure_demo_session()
        return True, None

    def get_user(self):
        return st.session_state.get("user")

    def create_session(self, user_id, title=None):
        current_time = datetime.now()
        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "user_id": user_id,
            "title": title
            or f"{current_time.strftime('%d-%m-%Y')} | {current_time.strftime('%H:%M:%S')}",
            "created_at": current_time.isoformat(),
        }
        sessions = st.session_state.local_chat_sessions.setdefault(user_id, [])
        sessions.insert(0, session_data)
        st.session_state.local_chat_messages.setdefault(session_id, [])
        return True, session_data

    def get_user_sessions(self, user_id):
        sessions = st.session_state.local_chat_sessions.get(user_id, [])
        return True, list(sessions)

    def save_chat_message(self, session_id, content, role="user"):
        messages = st.session_state.local_chat_messages.setdefault(session_id, [])
        message = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "content": content,
            "role": role,
            "created_at": datetime.now().isoformat(),
        }
        messages.append(message)
        return True, message

    def get_session_messages(self, session_id):
        return True, list(st.session_state.local_chat_messages.get(session_id, []))

    def delete_session(self, session_id):
        user = st.session_state.get("user")
        if not user:
            return False, "No active user"

        sessions = st.session_state.local_chat_sessions.get(user["id"], [])
        st.session_state.local_chat_sessions[user["id"]] = [
            session for session in sessions if session["id"] != session_id
        ]
        st.session_state.local_chat_messages.pop(session_id, None)
        return True, None

    def validate_session_token(self):
        return st.session_state.get("user") or self.ensure_demo_session()

    def get_user_data(self, user_id):
        return st.session_state.local_users.get(user_id)
