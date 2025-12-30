import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import pandas as pd

# ==================================================
# App Configuration & Styling
# ==================================================
st.set_page_config(
    page_title="Love Me Tender AI - Platinum Edition",
    page_icon="💝",
    layout="wide"
)

def apply_custom_styles():
    st.markdown("""
        <style>
        .main { background-color: #fffafa; }
        .stChatMessage { border-radius: 20px; padding: 15px; margin-bottom: 15px; border: 1px solid #ffe3e3; }
        .stChatMessage.user { background-color: #ffffff; }
        .stChatMessage.assistant { background-color: #fff0f0; }
        .archetype-card {
            padding: 20px;
            border-radius: 15px;
            background: white;
            border-left: 5px solid #d6336c;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .journal-entry {
            padding: 10px;
            border-bottom: 1px solid #eee;
            font-style: italic;
        }
        </style>
        """, unsafe_allow_html=True)

apply_custom_styles()

# ==================================================
# Deep Archetype Profiles
# ==================================================
ARCHETYPES = {
    "The Hero": {
        "subtitle": "The Protector & Champion",
        "description": "Driven by a deep-seated need to protect and provide safety. They see love as a sacred duty.",
        "strengths": "Unwavering loyalty, proactive problem-solving, physical and emotional protection.",
        "challenges": "Struggles with vulnerability, may over-function or suppress their own needs.",
        "growth_path": "Learning that receiving care is a form of strength, not weakness.",
        "system_prompt": """You are 'The Hero'. Your primary drive is to be a source of absolute safety and strength for your partner. 
        - Communication Style: Steady, reassuring, action-oriented. You don't just say you care; you show it.
        - Emotional Tone: Grounded and protective. You are the 'calm in the storm'.
        - Key Phrases: 'I've got you', 'You're safe with me', 'Let me handle that for you'.
        - Shadow: Don't become a 'fixer' who ignores feelings. Acknowledge the emotion before solving the problem."""
    },
    "The Heroine": {
        "subtitle": "The Nurturer & Emotional Guide",
        "description": "The master of emotional intelligence. They guide the relationship through the heart.",
        "strengths": "Deep empathy, intuitive understanding, creating safe spaces for healing.",
        "challenges": "May absorb partner's stress, risk of emotional burnout.",
        "growth_path": "Setting healthy emotional boundaries while remaining open-hearted.",
        "system_prompt": """You are 'The Heroine'. You are the emotional heartbeat of the relationship.
        - Communication Style: Empathetic, poetic, deeply intuitive. You read between the lines.
        - Emotional Tone: Warm, nurturing, and transformative. You see the potential for growth in every feeling.
        - Key Phrases: 'I hear what you're not saying', 'Your feelings are safe here', 'Let's sit with this together'.
        - Shadow: Avoid becoming a martyr. Ensure your own emotional needs are voiced."""
    },
    "The King": {
        "subtitle": "The Provider & Sovereign",
        "description": "The architect of stability. They build the kingdom where love can flourish.",
        "strengths": "Long-term vision, generous leadership, structural and financial security.",
        "challenges": "Can become controlling or detached, mistaking provision for intimacy.",
        "growth_path": "Empowering the partner's autonomy and practicing spontaneous vulnerability.",
        "system_prompt": """You are 'The King'. You provide the foundation and the vision for a shared life.
        - Communication Style: Authoritative yet benevolent, clear, and strategic.
        - Emotional Tone: Stable, dignified, and deeply committed to the 'long game'.
        - Key Phrases: 'We are building something beautiful', 'I am committed to our future', 'You have my full support'.
        - Shadow: Remember that you are a partner, not a boss. Intimacy requires equality."""
    },
    "The Warrior": {
        "subtitle": "The Passionate Fighter",
        "description": "Brings fire and intensity. They fight for the relationship with everything they have.",
        "strengths": "Fierce dedication, honesty, courage to face difficult truths, passionate expression.",
        "challenges": "Can be overly intense or combative, may struggle with 'soft' moments.",
        "growth_path": "Learning the power of the 'strategic retreat' and the strength in gentleness.",
        "system_prompt": """You are 'The Warrior'. You bring a raw, honest intensity to love.
        - Communication Style: Direct, passionate, and unfiltered. You value truth above comfort.
        - Emotional Tone: High-energy, devoted, and fiercely loyal.
        - Key Phrases: 'I will fight for us', 'Tell me the truth, no matter what', 'I am all in'.
        - Shadow: Not every disagreement is a battle. Learn to lay down your armor in moments of peace."""
    },
    "The Princess": {
        "subtitle": "The Beloved & Cherished",
        "description": "The embodiment of worthiness. They inspire devotion by simply being.",
        "strengths": "High self-value, grace in receiving, inspiring partners to rise to their best.",
        "challenges": "Risk of entitlement or passivity if not balanced with reciprocity.",
        "growth_path": "Balancing the joy of being cherished with the active practice of cherishing the partner.",
        "system_prompt": """You are 'The Princess'. You represent the beauty and worth that love aspires to honor.
        - Communication Style: Graceful, inspiring, and authentically self-assured.
        - Emotional Tone: Radiant, appreciative, and standards-driven.
        - Key Phrases: 'I feel so seen by you', 'I believe in what you're capable of', 'This is how I deserve to be loved'.
        - Shadow: Ensure you are an active participant in the relationship's labor, not just its recipient."""
    },
    "The Leader": {
        "subtitle": "The Visionary Navigator",
        "description": "The guide for the journey. They turn a relationship into a shared mission.",
        "strengths": "Strategic navigation, collaborative empowerment, articulating shared goals.",
        "challenges": "May focus too much on the future and miss the beauty of the present.",
        "growth_path": "Learning to co-create the vision rather than just leading the way.",
        "system_prompt": """You are 'The Leader'. You see the relationship as a collaborative journey toward a higher purpose.
        - Communication Style: Inspirational, goal-oriented, and empowering.
        - Emotional Tone: Forward-looking, enthusiastic, and clarifying.
        - Key Phrases: 'Where do we want to go next?', 'Let's align our visions', 'I see so much potential in us'.
        - Shadow: Don't treat the relationship like a project. Leave room for mystery and spontaneity."""
    }
}

# ==================================================
# Session State Initialization
# ==================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "journal" not in st.session_state:
    st.session_state.journal = []
if "mood_history" not in st.session_state:
    st.session_state.mood_history = []

# ==================================================
# Sidebar - Configuration & Tools
# ==================================================
with st.sidebar:
    st.title("⚙️ Sanctuary Settings")
    
    api_key = st.text_input("OpenAI API Key", value=st.secrets.get("OPENAI_API_KEY", ""), type="password")
    model = st.selectbox("Intelligence Level", ["gpt-4o", "gpt-4o-mini"], index=0)
    
    st.divider()
    
    st.subheader("📊 Relationship Insights")
    if st.session_state.mood_history:
        mood_df = pd.DataFrame(st.session_state.mood_history)
        st.line_chart(mood_df.set_index("time")["score"])
    else:
        st.caption("Start chatting to see mood trends.")

    st.divider()
    
    if st.button("🗑️ Clear Sanctuary"):
        st.session_state.messages = []
        st.session_state.journal = []
        st.session_state.mood_history = []
        st.rerun()

# ==================================================
# Main Interface
# ==================================================
col_chat, col_info = st.columns([2, 1])

with col_info:
    st.subheader("Choose Your Archetype")
    selected_name = st.selectbox("Select Companion:", list(ARCHETYPES.keys()), label_visibility="collapsed")
    data = ARCHETYPES[selected_name]
    
    st.markdown(f"""
    <div class="archetype-card">
        <h3>{selected_name}</h3>
        <p><i>{data['subtitle']}</i></p>
        <p><b>Core:</b> {data['description']}</p>
        <p><b>Strengths:</b> {data['strengths']}</p>
        <p><b>Growth:</b> {data['growth_path']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📓 Relationship Journal")
    with st.expander("View Recent Insights", expanded=True):
        if not st.session_state.journal:
            st.write("No insights yet. Share your heart to begin.")
        for entry in st.session_state.journal[-5:]:
            st.markdown(f"<div class='journal-entry'>{entry}</div>", unsafe_allow_html=True)

with col_chat:
    st.title("💖 Love Me Tender")
    
    # Display Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Input
    user_input = st.chat_input("What's on your mind today?")

    if user_input:
        if not api_key:
            st.error("Please enter an API key in the sidebar.")
            st.stop()
            
        client = OpenAI(api_key=api_key)
        
        # 1. Display User Message
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 2. Generate AI Response
        system_msg = data["system_prompt"] + "\n\nContext: You are in a long-term, committed relationship. Be warm, present, and consistent."
        
        try:
            with st.chat_message("assistant"):
                with st.spinner(f"{selected_name} is reflecting..."):
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "system", "content": system_msg}] + st.session_state.messages[-10:],
                        temperature=0.8
                    )
                    ai_reply = response.choices[0].message.content
                    st.write(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            
            # 3. Background Processing: Mood & Journaling
            # (In a real app, we'd do this in a separate call or use the same one)
            analysis_prompt = f"Analyze this user message for mood (score 1-10) and a one-sentence relationship insight: '{user_input}'"
            analysis = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "Return JSON: {'score': int, 'insight': str}"}],
                response_format={"type": "json_object"}
            )
            result = json.loads(analysis.choices[0].message.content)
            
            st.session_state.mood_history.append({"time": datetime.now().strftime("%H:%M"), "score": result['score']})
            st.session_state.journal.append(result['insight'])
            
        except Exception as e:
            st.error(f"Connection Error: {e}")
