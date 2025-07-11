import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_utils import get_all_sessions
#from redis_utils import get_all_threads
from api_utils import get_api_response


def display_sidebar():
    # Model selection                                                                         #selected_model added and supported_models added
    model_options = ["qwen3","gpt-4o", "gpt-4o-mini"] 

    supported_models = ["qwen3"]

    selected_m = st.sidebar.selectbox("Select Model", options=model_options, key="model")

    # Fallback to qwen3 if unsupported                                                         <-------]
    if selected_m not in supported_models:
        st.warning(f"Model '{selected_m}' is not available yet. Please switch back to 'qwen3'.")
        model_to_use = "qwen3"
    else:
        model_to_use = selected_m                                            

    # Conversation Threads Header
    st.sidebar.header("Conversation Threads")

    sessions = get_all_sessions()
    #sessions = get_all_threads()

    # Display each session like a chat item
    if sessions:
        for session in sessions:

            session_id = session["session_id"]
            title = session.get("title", "Untitled")
            label = f"{title[:30]}..." if len(title) > 30 else title


            if st.sidebar.button(label, key=f"session_{session_id}"):
                st.session_state.session_id = session_id
                st.session_state.messages = []

    # Add New Thread button at the end
    st.sidebar.markdown("---")
    if st.sidebar.button("🆕 Start New Thread"):
        st.session_state.session_id = None
        st.session_state.messages = []
