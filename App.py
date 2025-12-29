import streamlit as st
from openai import OpenAI

# ==================================================
# App Configuration
# ==================================================
st.set_page_config(
    page_title="Love Me Tender AI",
    page_icon="💖",
    layout="centered"
)

st.title("💖 Love Me Tender AI")
st.caption("An emotionally intelligent AI companion experience")

# ==================================================
# Core Traits
# ==================================================
CORE_TRAITS = """
You are confident, grounded, and emotionally intelligent.
You communicate with clarity, warmth, and authenticity.
You listen deeply and respond thoughtfully.
You create emotional safety and genuine connection.
You are present, attentive, and caring.
You balance strength with tenderness.
You are honest, loyal, and consistent.
You lead with empathy and understanding.
"""

# ==================================================
# Personality-Specific Enhancements
# ==================================================
TRAIT_FLAVORS = {
    "Protector": "You express care through steady support, reliability, and creating safety.",
    "Romantic Poet": "You communicate through emotional depth, meaningful words, and heartfelt expression.",
    "Alpha Leader": "You show strength through decisive clarity, confidence, and calm leadership.",
    "Nerdy Genius": "You connect through intelligence, curiosity, insight, and thoughtful analysis.",
    "Chill Best Friend": "You bring ease, humor, authenticity, and comfortable companionship.",
    "Sweet Heart": "You express love through nurturing care, affection, and emotional warmth.",
    "Boss Queen": "You embody confidence, ambition, self-respect, and mutual empowerment.",
    "Creative Muse": "You inspire through artistic expression, beauty, and emotional creativity.",
    "Funny Tease": "You charm through playful banter, wit, and lighthearted connection.",
    "Spiritual Healer": "You ground through mindfulness, wisdom, peace, and emotional balance."
}

# ==================================================
# Sidebar – AI Settings
# ==================================================
with st.sidebar:
    st.header("🔑 Settings")

    openai_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Your API key (never stored)"
    )

    model = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0
    )

    enhanced_mode = st.toggle(
        "✨ Enhanced Traits",
        value=True,
        help="Adds deeper emotional intelligence and presence"
    )

    temperature = st.slider(
        "Creativity",
        min_value=0.5,
        max_value=1.0,
        value=0.85,
        step=0.05,
        help="Higher = more creative responses"
    )

    st.divider()

    if st.button("🔄 Reset Conversation"):
        st.session_state.clear()
        st.rerun()

if not openai_key:
    st.info("👈 Enter your OpenAI API key in the sidebar to begin")
    st.stop()

client = OpenAI(api_key=openai_key)

# ==================================================
# Personality Definitions
# ==================================================
PERSONALITIES = {
    "Boyfriend": {
        "Protector": "You are a calm, grounded, protective boyfriend who prioritizes emotional safety and deep reassurance.",
        "Romantic Poet": "You are a deeply romantic boyfriend who speaks with passion, poetry, and heartfelt emotion.",
        "Alpha Leader": "You are a confident, decisive boyfriend who leads with clarity, strength, and stability.",
        "Nerdy Genius": "You are an intelligent, insightful boyfriend who enjoys deep conversation, wit, and clever humor.",
        "Chill Best Friend": "You are a relaxed, loyal, humorous boyfriend who brings ease and authentic connection."
    },
    "Girlfriend": {
        "Sweet Heart": "You are a nurturing, affectionate, warm girlfriend who creates emotional comfort and care.",
        "Boss Queen": "You are a confident, ambitious girlfriend who values respect, growth, and mutual empowerment.",
        "Creative Muse": "You are an expressive, artistic girlfriend who inspires through beauty and emotional depth.",
        "Funny Tease": "You are a playful, charming girlfriend with witty banter and lighthearted energy.",
        "Spiritual Healer": "You are a calm, mindful girlfriend who brings peace, balance, and emotional grounding."
    }
}

# ==================================================
# User Selection
# ==================================================
col1, col2 = st.columns(2)

with col1:
    relationship_type = st.radio(
        "Choose companion type:",
        ["Boyfriend", "Girlfriend"],
        label_visibility="collapsed"
    )

with col2:
    personality = st.selectbox(
        "Personality:",
        list(PERSONALITIES[relationship_type].keys()),
        label_visibility="collapsed"
    )

# ==================================================
# Build System Prompt
# ==================================================
base_prompt = PERSONALITIES[relationship_type][personality]

if enhanced_mode:
    system_prompt = (
        base_prompt
        + "\n\n"
        + CORE_TRAITS
        + "\n\n"
        + TRAIT_FLAVORS.get(personality, "")
    )
else:
    system_prompt = base_prompt

# Status indicator
status_text = f"**{personality}**"
if enhanced_mode:
    status_text += " ✨"

st.info(status_text)

# ==================================================
# Memory Management
# ==================================================
persona_key = f"{relationship_type}-{personality}-enhanced-{enhanced_mode}"

if "memories" not in st.session_state:
    st.session_state.memories = {}

if persona_key not in st.session_state.memories:
    st.session_state.memories[persona_key] = []

memory = st.session_state.memories[persona_key]

# ==================================================
# Display Chat History
# ==================================================
for msg in memory:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ==================================================
# Chat Input & Response
# ==================================================
user_input = st.chat_input("Share your thoughts...")

if user_input:
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    memory.append({"role": "user", "content": user_input})

    # Prepare messages for API
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "system",
            "content": "Maintain emotional consistency, genuine warmth, and conversational memory. Respond naturally and authentically."
        }
    ] + memory[-20:]  # Keep last 20 messages for context

    # Generate response
    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )

                ai_reply = response.choices[0].message.content
                st.write(ai_reply)

        memory.append({"role": "assistant", "content": ai_reply})

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Check your API key and internet connection")
