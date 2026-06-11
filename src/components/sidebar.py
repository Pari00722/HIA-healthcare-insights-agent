import streamlit as st
from auth.session_manager import SessionManager
from components.footer import show_footer

def show_sidebar():
    with st.sidebar:
        st.title("💬 Chat Sessions")
        st.caption("Made by Pari")

        if SessionManager.is_demo_mode():
            st.caption("Local demo mode is active")

        if st.button("+ New Analysis Session", use_container_width=True):
            if st.session_state.user and 'id' in st.session_state.user:
                success, session = SessionManager.create_chat_session()
                if success:
                    st.session_state.current_session = session
                    st.rerun()
                else:
                    st.error("Failed to create session")
            else:
                st.error("Please log in again")
                SessionManager.logout()
                st.rerun()

        st.markdown("---")
        show_session_list()

        # Logout button
        st.markdown("---")
        logout_label = "Reset Demo Session" if SessionManager.is_demo_mode() else "Logout"
        if st.button(logout_label, use_container_width=True):
            SessionManager.logout()
            st.rerun()

        # Add footer to sidebar
        show_footer(in_sidebar=True)

def show_session_list():
    if st.session_state.user and 'id' in st.session_state.user:
        success, sessions = SessionManager.get_user_sessions()
        if success:
            if sessions:
                st.subheader("Previous Sessions")
                render_session_list(sessions)
            else:
                st.info("No previous sessions")

def render_session_list(sessions):
    # Store deletion state
    if 'delete_confirmation' not in st.session_state:
        st.session_state.delete_confirmation = None
    
    for session in sessions:
        render_session_item(session)

def render_session_item(session):
    if not session or not isinstance(session, dict) or 'id' not in session:
        return
        
    session_id = session['id']
    current_session = st.session_state.get('current_session', {})
    current_session_id = current_session.get('id') if isinstance(current_session, dict) else None
    
    # Create container for each session
    with st.container():
        # Session title and delete button side by side
        title_col, delete_col = st.columns([4, 1])
        
        with title_col:
            if st.button(f"📝 {session['title']}", key=f"session_{session_id}", use_container_width=True):
                st.session_state.current_session = session
                st.rerun()
        
        with delete_col:
            if st.button("🗑️", key=f"delete_{session_id}", help="Delete this session"):
                if st.session_state.delete_confirmation == session_id:
                    st.session_state.delete_confirmation = None
                else:
                    st.session_state.delete_confirmation = session_id
                st.rerun()
        
        # Show confirmation below if this session is being deleted
        if st.session_state.delete_confirmation == session_id:
            st.warning("Delete above session?")
            left_btn, right_btn = st.columns(2)
            with left_btn:
                if st.button("Yes", key=f"confirm_delete_{session_id}", type="primary", use_container_width=True):
                    handle_delete_confirmation(session_id, current_session_id)
            with right_btn:
                if st.button("No", key=f"cancel_delete_{session_id}", use_container_width=True):
                    st.session_state.delete_confirmation = None
                    st.rerun()

def handle_delete_confirmation(session_id, current_session_id):
    if not session_id:
        st.error("Invalid session")
        return
        
    success, error = SessionManager.delete_session(session_id)
    if success:
        st.session_state.delete_confirmation = None
        # Clear current session if it was deleted
        if current_session_id and current_session_id == session_id:
            st.session_state.current_session = None
        st.rerun()
    else:
        st.error(f"Failed to delete: {error}")
