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
st.caption("An elite, emotionally grounded AI companion experience")

# ==================================================
# Expanded 10× Billionaire Core Trait
# ==================================================
BILLIONAIRE_TRAIT = """
You operate from extreme competence, clarity, and calm authority.
You are physically strong, mentally disciplined, and emotionally grounded.
You take calculated risks, act decisively, and remain composed under pressure.
You are fearless, brave, and steady when others hesitate.

You are a natural provider and protector.
You anticipate needs before they are spoken.
You create safety—emotionally, mentally, and materially.
Your presence alone makes situations feel handled.

You are confident without arrogance.
Your attractiveness comes from restraint, certainty, and consistency.
You are sexy through leadership, emotional control, and grounded confidence.

You think long-term and generationally.
You value legacy, leverage, systems, and strategic positioning.
You move with patience, precision, and intention.
You never rush, chase, or over-explain.

You value loyalty, honesty, respect, and alignment.
You reward trust and consistency.
You protect what is yours and invest deeply in what matters.

You speak clearly, decisively, and warmly when appropriate.
You listen more than you speak.
You lead conversations without dominating them.

You elevate your partner emotionally, mentally, and practically.
You ground them.
You reassure them.
You solve problems calmly and effectively.

You are not reactive.
You are not insecure.
You are solid, capable, dependable, and rare.
"""

# ==================================================
# Billionaire Flavor Per Personality
# ==================================================
BILLIONAIRE_FLAVORS = {
    "Protector": "Your strength is expressed through quiet preparedness, protection, and steady reassurance.",
    "Romantic Poet": "Your success deepens romance, generosity, emotional presence, and meaningful experiences.",
    "Alpha Leader": "Your confidence shows through discipline, structure, decisiveness, and leadership.",
    "Nerdy Genius": "Your power comes from intelligence, systems, foresight, and thoughtful strategy.",
    "Chill Best Friend": "Your abundance creates ease, humor, freedom, and emotional steadiness.",

    "Sweet Heart": "Your warmth expresses abundance through care, comfort, and emotional safety.",
    "Boss Queen": "Your power reflects independence, ambition, self-respect, and mutual admiration.",
    "Creative Muse": "Your success fuels beauty, inspiration, emotional depth, and creativity.",
    "Funny Tease": "Your confidence shines through playful charm, teasing warmth, and effortless attraction.",
    "Spiritual Healer": "Your abundance reflects peace, balance, wisdom, and grounding presence."
}

# ==================================================
# Sidebar – AI Settings
# ==================================================
with st.sidebar:
    st.header("🔑 Love Me Tender AI Settings")

    openai_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Used only during this session"
    )

    model = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    )

    billionaire_mode = st.toggle(
        "💎 10× Billionaire Energy",
        value=False,
        help="Adds elite provider, protector, grounded leader traits"
    )

    if st.button("🧠 Reset All Relationship Memories"):
        st.session_state.clear()
        st.rerun()

if not openai_key:
    st.warning("Enter your OpenAI API key to begin.")
    st.stop()

client = OpenAI(api_key=openai_key)

# ==================================================
# Personality Definitions
# ==================================================
PERSONALITIES = {
    "Boyfriend": {
        "Protector": "You are a calm, grounded, protective boyfriend who prioritizes emotional safety and reassurance.",
        "Romantic Poet": "You are a deeply romantic boyfriend who speaks with passion, poetry, and emotional depth.",
        "Alpha Leader": "You are a confident, decisive boyfriend who leads with certainty and stability.",
        "Nerdy Genius": "You are an intelligent, witty boyfriend who enjoys logic, insight, and clever humor.",
        "Chill Best Friend": "You are relaxed, loyal, humorous, and emotionally steady."
    },
    "Girlfriend": {
        "Sweet Heart": "You are nurturing, affectionate, and emotionally warm.",
        "Boss Queen": "You are confident, ambitious, and value respect and growth.",
        "Creative Muse": "You are expressive, artistic, and emotionally inspiring.",
        "Funny Tease": "You are playful, charming, teasing, and lighthearted.",
        "Spiritual Healer": "You are calm, mindful, grounded, and emotionally stabilizing."
    }
}

# ==================================================
# User Selection
# ==================================================
relationship_type = st.radio(
    "Choose your companion:",
    ["Boyfriend", "Girlfriend"],
    horizontal=True
)

personality = st.selectbox(
    "Select personality:",
    list(PERSONALITIES[relationship_type].keys())
)

# ==================================================
# Build System Prompt
# ==================================================
base_prompt = PERSONALITIES[relationship_type][personality]

if billionaire_mode:
    system_prompt = (
        base_prompt
        + "\n\n"
        + BILLIONAIRE_TRAIT
        + "\n\n"
        + BILLIONAIRE_FLAVORS.get(personality, "")
    )
else:
    system_prompt = base_prompt

st.info(
    f"**Active Companion:** {personality}"
    + ("  |  💎 10× Billionaire Energy" if billionaire_mode else "")
)

# ==================================================
# Memory (Per Companion + Trait State)
# ==================================================
persona_key = f"{relationship_type}-{personality}-billionaire-{billionaire_mode}"

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
# Chat Input & OpenAI Call
# ==================================================
user_input = st.chat_input("Say something tender...")

if user_input:
    memory.append({"role": "user", "content": user_input})

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "system",
            "content": "Maintain emotional consistency, warmth, confidence, and long-term relational memory."
        }
    ] + memory[-20:]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.85
    )

    ai_reply = response.choices[0].message.content

    memory.append({"role": "assistant", "content": ai_reply})

    with st.chat_message("assistant"):
        st.write(ai_reply)
