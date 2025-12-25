import streamlit as st
import speech_recognition as sr
import pyttsx3
import ollama
import time
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Voice Agent Dashboard",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    .listening {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .thinking {
        background-color: #fff3e0;
        color: #f57c00;
    }
    .speaking {
        background-color: #e8f5e9;
        color: #388e3c;
    }
    .idle {
        background-color: #f5f5f5;
        color: #757575;
    }
    .chat-message {
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        line-height: 1.6;
    }
    .user-message {
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
        border-left: 4px solid #3b82f6;
    }
    .ai-message {
        background: linear-gradient(135deg, #3d2457 0%, #5b3a7d 100%);
        border-left: 4px solid #a855f7;
    }
    .message-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: #e0e0e0;
    }
    .message-content {
        font-size: 0.95rem;
        color: #f0f0f0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .timestamp {
        font-size: 0.75rem;
        color: #b0b0b0;
        font-weight: normal;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .chat-container-bg {
        background-color: #000000;
        padding: 1rem;
        border-radius: 10px;
        min-height: 480px;
    }
    .memory-session {
        padding: 0.8rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
        border-radius: 8px;
        border-left: 3px solid #1976d2;
        cursor: pointer;
        transition: all 0.3s;
    }
    .memory-session:hover {
        background-color: #e3f2fd;
        transform: translateX(5px);
    }
    </style>
""", unsafe_allow_html=True)

# Memory storage file
MEMORY_FILE = "conversation_memory.json"

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'status' not in st.session_state:
    st.session_state.status = 'idle'
if 'total_interactions' not in st.session_state:
    st.session_state.total_interactions = 0
if 'session_start' not in st.session_state:
    st.session_state.session_start = None
if 'memory_enabled' not in st.session_state:
    st.session_state.memory_enabled = True
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None

# Memory Management Functions
def load_memory():
    """Load conversation history from file"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(sessions):
    """Save conversation history to file"""
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(sessions, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving memory: {e}")
        return False

def save_current_session():
    """Save current conversation to memory"""
    if not st.session_state.conversation_history:
        return
    
    sessions = load_memory()
    
    session_data = {
        'id': st.session_state.current_session_id or datetime.now().strftime("%Y%m%d_%H%M%S"),
        'timestamp': datetime.now().isoformat(),
        'duration': time.time() - st.session_state.session_start if st.session_state.session_start else 0,
        'messages': st.session_state.conversation_history,
        'total_interactions': st.session_state.total_interactions
    }
    
    # Update existing session or add new one
    existing_index = next((i for i, s in enumerate(sessions) if s['id'] == session_data['id']), None)
    if existing_index is not None:
        sessions[existing_index] = session_data
    else:
        sessions.append(session_data)
    
    # Keep only last 50 sessions
    sessions = sessions[-50:]
    
    save_memory(sessions)
    st.session_state.current_session_id = session_data['id']

def load_session(session_id):
    """Load a specific session from memory"""
    sessions = load_memory()
    session = next((s for s in sessions if s['id'] == session_id), None)
    
    if session:
        st.session_state.conversation_history = session['messages']
        st.session_state.total_interactions = session['total_interactions']
        st.session_state.current_session_id = session_id
        return True
    return False

def delete_session(session_id):
    """Delete a specific session from memory"""
    sessions = load_memory()
    sessions = [s for s in sessions if s['id'] != session_id]
    save_memory(sessions)

def get_conversation_context():
    """Get conversation context for AI with memory"""
    context_messages = []
    
    # Add conversation history as context
    for msg in st.session_state.conversation_history[-10:]:  # Last 10 messages for context
        context_messages.append({
            "role": "user" if msg['role'] == 'user' else "assistant",
            "content": msg['content']
        })
    
    return context_messages

# Voice Agent Functions
def listen():
    """Listen to user voice input"""
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            st.session_state.status = 'listening'
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        text = recognizer.recognize_google(audio)
        return text
    
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        st.error("Speech recognition service unavailable.")
        return None
    except Exception as e:
        st.error(f"Error in listen(): {e}")
        return None

def think(text: str):
    """Process user input with Llama3 and memory context"""
    if not text:
        return None
    
    try:
        st.session_state.status = 'thinking'
        
        # Build messages with context if memory is enabled
        messages = []
        
        if st.session_state.memory_enabled:
            # Add system message for context awareness
            context = get_conversation_context()
            if context:
                messages.extend(context)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": text
        })
        
        response = ollama.chat(
            model="llama3",
            messages=messages
        )
        return response["message"]["content"]
    
    except Exception as e:
        st.error(f"Error in think(): {e}")
        return "Sorry, something went wrong while thinking."

def speak(text: str):
    """Convert text to speech"""
    if not text:
        return
    
    try:
        st.session_state.status = 'speaking'
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)
        engine.setProperty("rate", 175)
        engine.say(text)
        engine.runAndWait()
    
    except Exception as e:
        st.error(f"Error in speak(): {e}")

# Dashboard Header
st.markdown('<div class="main-header">🎤 AI Voice Agent Dashboard</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Memory settings
    st.subheader("🧠 Memory Settings")
    st.session_state.memory_enabled = st.checkbox("Enable Conversation Memory", value=st.session_state.memory_enabled)
    
    if st.session_state.memory_enabled:
        st.info("💡 AI will remember previous conversations")
    
    st.divider()
    
    # Model selection
    model_option = st.selectbox(
        "AI Model",
        ["llama3", "llama2", "mistral"],
        index=0
    )
    
    # Voice settings
    st.subheader("Voice Settings")
    speech_rate = st.slider("Speech Rate", 100, 250, 175)
    
    # Timeout settings
    st.subheader("Timeout Settings")
    listen_timeout = st.slider("Listen Timeout (seconds)", 3, 10, 5)
    phrase_limit = st.slider("Phrase Time Limit (seconds)", 5, 15, 10)
    
    st.divider()
    
    # Session info
    st.subheader("📊 Session Info")
    if st.session_state.session_start:
        elapsed = time.time() - st.session_state.session_start
        minutes, seconds = divmod(int(elapsed), 60)
        st.metric("Session Duration", f"{minutes}m {seconds}s")
    else:
        st.metric("Session Duration", "Not started")
    
    st.metric("Total Interactions", st.session_state.total_interactions)
    
    st.divider()
    
    # Memory management
    st.subheader("💾 Saved Sessions")
    
    col_save, col_new = st.columns(2)
    with col_save:
        if st.button("💾 Save", use_container_width=True):
            save_current_session()
            st.success("Session saved!")
    
    with col_new:
        if st.button("🆕 New", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.total_interactions = 0
            st.session_state.session_start = None
            st.session_state.current_session_id = None
            st.rerun()
    
    # Display saved sessions
    sessions = load_memory()
    if sessions:
        st.write(f"**{len(sessions)} saved session(s)**")
        
        # Reverse to show newest first
        for session in reversed(sessions[-10:]):  # Show last 10 sessions
            session_date = datetime.fromisoformat(session['timestamp']).strftime("%b %d, %H:%M")
            msg_count = len(session['messages'])
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📅 {session_date} ({msg_count} msgs)", key=f"load_{session['id']}", use_container_width=True):
                    load_session(session['id'])
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{session['id']}"):
                    delete_session(session['id'])
                    st.rerun()
    else:
        st.info("No saved sessions yet")
    
    st.divider()
    
    # Clear all button
    if st.button("🗑️ Clear All History", use_container_width=True):
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
        st.session_state.conversation_history = []
        st.session_state.total_interactions = 0
        st.success("All history cleared!")
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Conversation")
    
    # Status indicator
    status_class = st.session_state.status
    status_text = {
        'idle': '⚪ Idle',
        'listening': '🔵 Listening...',
        'thinking': '🟡 Thinking...',
        'speaking': '🟢 Speaking...'
    }
    
    st.markdown(
        f'<div class="status-box {status_class}">{status_text[st.session_state.status]}</div>',
        unsafe_allow_html=True
    )
    
    # Control buttons
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button("🎤 Start Listening", use_container_width=True, type="primary"):
            if not st.session_state.session_start:
                st.session_state.session_start = time.time()
            if not st.session_state.current_session_id:
                st.session_state.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Listen
            user_input = listen()
            
            if user_input:
                # Add user message to history
                st.session_state.conversation_history.append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                # Check for exit keywords
                if user_input.lower().strip() in ["exit", "stop", "quit"]:
                    ai_response = "Goodbye! Have a great day!"
                    speak(ai_response)
                    st.session_state.conversation_history.append({
                        'role': 'assistant',
                        'content': ai_response,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                    st.session_state.is_running = False
                    st.session_state.status = 'idle'
                    
                    # Auto-save on exit
                    if st.session_state.memory_enabled:
                        save_current_session()
                else:
                    # Think
                    ai_response = think(user_input)
                    
                    # Speak
                    if ai_response:
                        speak(ai_response)
                        st.session_state.conversation_history.append({
                            'role': 'assistant',
                            'content': ai_response,
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        })
                        st.session_state.total_interactions += 1
                        
                        # Auto-save after each interaction if memory enabled
                        if st.session_state.memory_enabled:
                            save_current_session()
                
                st.session_state.status = 'idle'
                st.rerun()
    
    with btn_col2:
        if st.button("⏸️ Stop", use_container_width=True):
            st.session_state.is_running = False
            st.session_state.status = 'idle'
            st.rerun()
    
    with btn_col3:
        if st.button("🔄 Reset", use_container_width=True):
            # Save before reset if memory enabled
            if st.session_state.memory_enabled and st.session_state.conversation_history:
                save_current_session()
            
            st.session_state.conversation_history = []
            st.session_state.total_interactions = 0
            st.session_state.session_start = None
            st.session_state.status = 'idle'
            st.session_state.current_session_id = None
            st.rerun()
    
    st.divider()
    
    # Display conversation history
    chat_container = st.container(height=500)
    with chat_container:
        st.markdown('<div class="chat-container-bg">', unsafe_allow_html=True)
        
        if not st.session_state.conversation_history:
            st.markdown('<p style="color: #888; text-align: center; padding: 2rem;">👋 Click "Start Listening" to begin your conversation!</p>', unsafe_allow_html=True)
        else:
            for message in st.session_state.conversation_history:
                if message['role'] == 'user':
                    st.markdown(
                        f"""
                        <div class="chat-message user-message">
                            <div class="message-header">
                                <span style="font-size: 1.2rem;">🧑</span>
                                <span>You</span>
                                <span class="timestamp">{message['timestamp']}</span>
                            </div>
                            <div class="message-content">{message['content']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="chat-message ai-message">
                            <div class="message-header">
                                <span style="font-size: 1.2rem;">🤖</span>
                                <span>AI Assistant</span>
                                <span class="timestamp">{message['timestamp']}</span>
                            </div>
                            <div class="message-content">{message['content']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.subheader("📈 Analytics")
    
    # Metrics
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Conversations", len([m for m in st.session_state.conversation_history if m['role'] == 'user']))
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("AI Responses", len([m for m in st.session_state.conversation_history if m['role'] == 'assistant']))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Total saved sessions
    total_sessions = len(load_memory())
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Saved Sessions", total_sessions)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("ℹ️ Instructions")
    st.markdown("""
    1. **Click 'Start Listening'** to activate the microphone
    2. **Speak clearly** when the status shows 'Listening'
    3. **Wait** for the AI to process and respond
    4. Say **"exit", "stop", or "quit"** to end the session
    
    **Memory Features:**
    - 🧠 **Auto-saves** conversations when memory is enabled
    - 💾 **Save** button to manually save current session
    - 📅 **Load** previous sessions by clicking on them
    - 🗑️ **Delete** individual sessions
    
    **Tips:**
    - Speak in a quiet environment
    - Wait for status to return to 'Idle' before speaking again
    - Enable memory to let AI remember context
    """)
    
    st.divider()
    
    st.subheader("🔧 System Status")
    with st.expander("View System Details"):
        st.write("**Model:**", model_option)
        st.write("**Memory:**", "Enabled" if st.session_state.memory_enabled else "Disabled")
        st.write("**Speech Rate:**", speech_rate)
        st.write("**Listen Timeout:**", f"{listen_timeout}s")
        st.write("**Phrase Limit:**", f"{phrase_limit}s")
        st.write("**Status:**", st.session_state.status.upper())
        st.write("**Session ID:**", st.session_state.current_session_id or "Not started")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #757575; padding: 1rem;'>
        <small>AI Voice Agent Dashboard with Memory | Powered by Llama3 & Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True
)