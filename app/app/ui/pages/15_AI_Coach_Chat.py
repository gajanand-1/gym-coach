import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css
from app.utils.session import require_login, init_session_defaults
from app.models.database import SessionLocal
from app.storage.chat_store import ChatStore
from app.graph.coach_chat_graph import run_coach_chat_graph

st.set_page_config(page_title="AI Coach Chat", page_icon="🤖", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 🤖 AI Coach Chat")
st.markdown("Your personal AI trainer, nutritionist & progress coach — with full knowledge of your data.")
st.divider()

# ── Session management ───────────────────────────────────────────────────
session_id = st.session_state.get("chat_session_id", "default")

col_clear, col_session = st.columns([2, 5])
with col_clear:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        db_c = SessionLocal()
        ChatStore(db_c).clear_session(user_id, session_id)
        db_c.close()
        st.rerun()
with col_session:
    st.caption(f"Session: `{session_id}`")

# ── Load chat history ────────────────────────────────────────────────────
db = SessionLocal()
chat_store = ChatStore(db)
messages = chat_store.get_as_langchain_messages(user_id, session_id, limit=40)
db.close()

# ── Render history ───────────────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not messages:
        st.markdown(
            '<div class="chat-ai">'
            '👋 Hi! I\'m your AI Coach. I have access to all your fitness data — '
            'food logs, workouts, weight, sleep, and your goals.<br><br>'
            'Ask me anything:<br>'
            '• "What should I eat for dinner to hit my protein target?"<br>'
            '• "Why is my weight not dropping?"<br>'
            '• "Should I increase my bench press weight?"<br>'
            '• "Am I on track to reach my goal?"'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                st.markdown(
                    f'<div class="chat-user">🧑 {content}</div>',
                    unsafe_allow_html=True,
                )
            elif role == "assistant":
                st.markdown(
                    f'<div class="chat-ai">🤖 {content}</div>',
                    unsafe_allow_html=True,
                )

# ── Input ────────────────────────────────────────────────────────────────
st.divider()

# Quick prompts
st.markdown("**Quick Questions:**")
q_cols = st.columns(4)
quick_prompts = [
    "What should I eat today?",
    "Am I hitting my protein target?",
    "Should I increase my bench press?",
    "Why is my weight not dropping?",
]
for col, prompt in zip(q_cols, quick_prompts):
    if col.button(prompt, use_container_width=True):
        st.session_state["chat_input_prefill"] = prompt

user_input = st.chat_input(
    placeholder="Ask your AI coach anything…",
)

# Handle quick prompt pre-fill
if "chat_input_prefill" in st.session_state:
    user_input = st.session_state.pop("chat_input_prefill")

if user_input and user_input.strip():
    with st.spinner("🤖 Coach is thinking..."):
        result = run_coach_chat_graph(
            user_id=user_id,
            user_message=user_input.strip(),
            session_id=session_id,
        )
    if result.get("error") and not result.get("response"):
        st.error(f"Error: {result['error']}")
    else:
        st.rerun()
