import streamlit as st
import requests
from datetime import datetime, timedelta
from pathlib import Path
import time
import os

# Configuration
API_BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    "query": f"{API_BASE_URL}/api/v1/chat/query",
    "sessions": f"{API_BASE_URL}/api/v1/chat/sessions",
    "session_detail": f"{API_BASE_URL}/api/v1/chat/sessions/{{session_id}}/full",
    "delete_session": f"{API_BASE_URL}/api/v1/chat/sessions/{{session_id}}",
    "clear_memory": f"{API_BASE_URL}/api/v1/chat/memory/{{session_id}}/clear",
}

# Page config
st.set_page_config(
    page_title="RAG Chat Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Delete button styling */
    button[kind="secondary"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        color: #666 !important;
        font-size: 1.5rem !important;
        min-height: auto !important;
        height: auto !important;
    }
    button[kind="secondary"]:hover {
        color: #ff4b4b !important;
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Citation box styling */
    .citation-container {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .citation-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        background-color: #dbeafe;
        border-left: 3px solid #3b82f6;
        border-radius: 4px;
        margin-bottom: 0.75rem;
    }
    
    .citation-title {
        font-weight: 600;
        color: #1e40af;
        font-size: 0.95rem;
    }
    
    .citation-meta {
        color: #64748b;
        font-size: 0.85rem;
        margin: 0.25rem 0;
    }
    
    .citation-content {
        background-color: white;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #e2e8f0;
        margin-top: 0.5rem;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .citation-content h1, .citation-content h2, .citation-content h3 {
        color: #1f2937;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .citation-content p {
        color: #374151;
        line-height: 1.6;
        margin-bottom: 0.75rem;
    }
    
    .citation-content ul, .citation-content ol {
        margin-left: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    .citation-content code {
        background-color: #f3f4f6;
        padding: 0.125rem 0.25rem;
        border-radius: 3px;
        font-size: 0.9em;
    }
    
    .citation-content pre {
        background-color: #f3f4f6;
        padding: 0.75rem;
        border-radius: 4px;
        overflow-x: auto;
    }
    
    /* Metadata styling */
    .metadata-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin-top: 0.5rem;
        font-size: 0.8rem;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "current_session_name" not in st.session_state:
        st.session_state.current_session_name = "New Chat"
    if "user_id" not in st.session_state:
        st.session_state.user_id = "streamlit_user"
    if "sessions_list" not in st.session_state:
        st.session_state.sessions_list = []
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}

# Helper Functions
def create_new_session():
    """Create a new chat session"""
    st.session_state.messages = []
    st.session_state.current_session_id = None
    st.session_state.current_session_name = "New Chat"

def load_session(session_id: str):
    """Load an existing session"""
    try:
        response = requests.get(
            API_ENDPOINTS["session_detail"].format(session_id=session_id)
        )
        if response.status_code == 200:
            session_data = response.json()
            st.session_state.current_session_id = session_data["session_id"]
            st.session_state.current_session_name = session_data["session_name"]
            
            # Load messages
            st.session_state.messages = []
            for msg in session_data.get("messages", []):
                st.session_state.messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                    "metadata": msg.get("metadata", {})
                })
            
            st.session_state.conversations[session_id] = session_data
            return True
        return False
    except Exception as e:
        st.error(f"Error loading session: {str(e)}")
        return False

def get_all_sessions():
    """Fetch all sessions from API"""
    try:
        response = requests.get(f"{API_ENDPOINTS['sessions']}/all?limit=50")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching sessions: {str(e)}")
        return []

def delete_session(session_id: str):
    """Delete a session"""
    try:
        response = requests.delete(
            API_ENDPOINTS["delete_session"].format(session_id=session_id)
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error deleting session: {str(e)}")
        return False

def clear_session_memory(session_id: str):
    """Clear memory for a session"""
    try:
        response = requests.post(
            API_ENDPOINTS["clear_memory"].format(session_id=session_id)
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error clearing memory: {str(e)}")
        return False

def send_message(message: str):
    """Send message to API and get response"""
    try:
        payload = {
            "query": message,
            "session_id": st.session_state.current_session_id,
            "user_id": st.session_state.user_id
        }
        
        response = requests.post(API_ENDPOINTS["query"], json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return None

def categorize_sessions(sessions):
    """Categorize sessions into Today, This Week, and Older"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    
    categorized = {
        "Today": [],
        "This Week": [],
        "Older": []
    }
    
    for session in sessions:
        try:
            last_chat_str = session.get('last_chat_datetime', session.get('updated_at', ''))
            if last_chat_str:
                last_chat = datetime.fromisoformat(last_chat_str.replace('Z', '+00:00'))
                last_chat = last_chat.replace(tzinfo=None)
                
                if last_chat >= today_start:
                    categorized["Today"].append(session)
                elif last_chat >= week_start:
                    categorized["This Week"].append(session)
                else:
                    categorized["Older"].append(session)
            else:
                categorized["Older"].append(session)
        except Exception:
            categorized["Older"].append(session)
    
    return categorized

def display_welcome_section():
    """Display the welcome section"""
    st.markdown("""
        <div style='text-align: center; padding: 2rem; margin: 2rem;'>
            <div style='background-color: #3b82f6; border-radius: 50%; width: 150px; height: 150px; 
                      margin: 0 auto; display: flex; align-items: center; justify-content: center;
                      border: 2px solid #1e40af;'>
                <span style='font-size: 3rem; color: white;'>💬</span>
            </div>
            <div style='margin-top: 1.5rem; font-size: 2rem; font-weight: 600; color: #1f2937;'>
                RAG Chat Assistant
            </div>
            <div style='margin-top: 0.5rem; color: #6b7280; font-size: 1.1rem;'>
                Ask questions and get answers from your documents 📚
            </div>
            <div style='margin-top: 1rem; color: #9ca3af; font-size: 0.9rem;'>
                Start a conversation by typing a message below
            </div>
        </div>
    """, unsafe_allow_html=True)

def read_citation_html(citation_path: str) -> str:
    """Read HTML citation file and return content"""
    try:
        if os.path.exists(citation_path):
            with open(citation_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    except Exception as e:
        st.error(f"Error reading citation file: {str(e)}")
        return None

def render_citations(citations):
    """Render citations with HTML content"""
    if not citations:
        return
    
    st.markdown("### 📚 Citations")
    st.caption(f"{len(citations)} source{'s' if len(citations) > 1 else ''} found")
    
    for idx, citation in enumerate(citations, 1):
        file_id = citation.get("file_id", "Unknown")
        chunk_id = citation.get("chunk_id", "N/A")
        page = citation.get("page", "N/A")
        header = citation.get("header", "No header")
        citation_path = citation.get("citation_path", "")
        
        # Create citation container
        with st.container():
            # Citation header
            header_html = f"""
            <div class="citation-header">
                <span style="font-size: 1.2rem;">📄</span>
                <div>
                    <div class="citation-title">Source {idx}</div>
                    <div class="citation-meta">Page: {page} | Chunk: {chunk_id}</div>
                </div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)
            
            # Read and display citation content
            if citation_path and os.path.exists(citation_path):
                html_content = read_citation_html(citation_path)
                if html_content:
                    # Display in expander for better organization
                    with st.expander("📖 View Full Citation", expanded=False):
                        st.markdown(f'<div class="citation-content">{html_content}</div>', unsafe_allow_html=True)
                else:
                    st.warning("Citation content not available")
            else:
                st.warning(f"Citation file not found: {citation_path}")
            
            st.markdown("---")

def render_metadata(metadata):
    """Render message metadata"""
    if not metadata:
        return
    
    info_parts = []
    if metadata.get("files_used"):
        info_parts.append(f"📁 {metadata['files_used']} file{'s' if metadata['files_used'] > 1 else ''}")
    if metadata.get("citation_required"):
        citation_count = len(metadata.get('citations', []))
        info_parts.append(f"📎 {citation_count} citation{'s' if citation_count > 1 else ''}")
    if metadata.get("memory_used"):
        info_parts.append("🧠 Memory used")
    if metadata.get("chunks_retrieved"):
        info_parts.append(f"🔍 {metadata['chunks_retrieved']} chunks retrieved")
    
    if info_parts:
        metadata_html = f"""
        <div class="metadata-box">
            {" • ".join(info_parts)}
        </div>
        """
        st.markdown(metadata_html, unsafe_allow_html=True)

def display_message_with_metadata(message, role):
    """Display a chat message with optional citations"""
    with st.chat_message(role):
        st.markdown(message.get("content", ""))
        
        if role == "assistant":
            metadata = message.get("metadata", {})
            
            # Render metadata first
            render_metadata(metadata)
            
            # Then render citations if available
            if metadata.get("citations"):
                st.markdown("")  # Add spacing
                render_citations(metadata["citations"])

def main():
    init_session_state()

    # Sidebar - Session Management
    with st.sidebar:
        st.title("💬 Chats")
        
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            create_new_session()
            st.rerun()
        
        st.divider()
        
        # Settings
        with st.expander("⚙️ Settings"):
            st.session_state.user_id = st.text_input(
                "User ID", 
                value=st.session_state.user_id
            )
            
            if st.session_state.current_session_id:
                if st.button("🧹 Clear Memory", use_container_width=True):
                    if clear_session_memory(st.session_state.current_session_id):
                        st.success("Memory cleared!")
                        st.rerun()
                
                if st.button("🗑️ Delete Current Session", use_container_width=True):
                    if delete_session(st.session_state.current_session_id):
                        st.success("Session deleted!")
                        create_new_session()
                        st.rerun()
        
        st.divider()
        
        # Fetch sessions if not loaded
        if not st.session_state.sessions_list:
            st.session_state.sessions_list = get_all_sessions()
        
        # Categorize and display sessions
        categorized_sessions = categorize_sessions(st.session_state.sessions_list)
        
        for category, sessions in categorized_sessions.items():
            if sessions:
                st.markdown(f"**{category}**")
                
                for session in sessions:
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        session_name = session.get('session_name', 'Unnamed Session')
                        is_active = session['session_id'] == st.session_state.current_session_id
                        
                        if st.button(
                            session_name[:35],
                            key=f"session_{session['session_id']}",
                            use_container_width=True,
                            type="primary" if is_active else "secondary"
                        ):
                            if load_session(session['session_id']):
                                st.rerun()
                    
                    with col2:
                        if st.button(
                            "×", 
                            key=f"delete_{session['session_id']}", 
                            help="Delete session",
                            type="secondary"
                        ):
                            if delete_session(session['session_id']):
                                st.session_state.sessions_list = get_all_sessions()
                                if session['session_id'] == st.session_state.current_session_id:
                                    create_new_session()
                                st.rerun()
                    
                    # Show message count
                    msg_count = session.get('message_count', 0)
                    st.caption(f"💬 {msg_count} messages")
                
                st.write("")

    # Main Chat Interface
    if not st.session_state.current_session_id:
        display_welcome_section()
    else:
        # Display session header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title(f"💬 {st.session_state.current_session_name}")
        with col2:
            session_data = st.session_state.conversations.get(st.session_state.current_session_id)
            if session_data and session_data.get('last_chat_time_ago'):
                st.caption(f"Last activity: {session_data['last_chat_time_ago']}")
        
        st.divider()
        
        # Display chat messages
        for message in st.session_state.messages:
            display_message_with_metadata(message, message["role"])

    # Chat input
    prompt = st.chat_input("Type your message here...")
    if prompt:
        # Add user message
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt, 
            "metadata": {}
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Show spinner with assistant message
        with st.chat_message("assistant"):
            spinner_messages = [
                "Thinking...",
                "Searching documents...",
                "Analyzing context...",
                "Generating answer..."
            ]
            
            spinner_placeholder = st.empty()
            
            for msg in spinner_messages:
                spinner_placeholder.markdown(f"*{msg}*")
                time.sleep(0.5)
            
            # Get response
            response = send_message(prompt)
            
            spinner_placeholder.empty()
            
            if response:
                # Update session info
                st.session_state.current_session_id = response["session_id"]
                st.session_state.current_session_name = response.get("session_name", "New Chat")
                
                # Display response
                st.markdown(response["answer"])
                
                # Prepare metadata
                metadata = {
                    "citation_required": response.get("citation_required", False),
                    "citation_limit": response.get("citation_limit", 0),
                    "files_used": response.get("files_used", 0),
                    "citations": response.get("citations", []),
                    "memory_used": response.get("memory_used", False),
                    "chunks_retrieved": response.get("chunks_retrieved", 0)
                }
                
                # Render metadata
                render_metadata(metadata)
                
                # Render citations if available
                if metadata["citations"]:
                    st.markdown("")  # Add spacing
                    render_citations(metadata["citations"])
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "metadata": metadata
                })
                
                # Refresh sessions list
                st.session_state.sessions_list = get_all_sessions()
                st.rerun()
            else:
                st.error("Failed to get response from the API")

    # Footer
    st.divider()
    st.caption("Powered by FastAPI RAG Backend | Built with Streamlit")

if __name__ == "__main__":
    main()