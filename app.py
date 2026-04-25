import streamlit as st
from dotenv import load_dotenv
import os
import requests
from langchain_groq import ChatGroq

load_dotenv()

# ------------------- LLM -------------------
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.9)

# ------------------- CHATBOT -------------------
def get_reply(user_input, personality):

    if personality == "Angry":
        personality_prompt = "You are rude, impatient, slightly aggressive."
    elif personality == "Flirty":
        personality_prompt = "You are playful, charming, slightly flirty."
    elif personality == "Teacher":
        personality_prompt = "You explain things clearly like a strict teacher."
    elif personality == "Sarcastic":
        personality_prompt = "You are sarcastic, funny, and witty."
    else:
        personality_prompt = "You are kind, friendly, and helpful."

    prompt = f"""
You are a chatbot.

{personality_prompt}

Rules:
- Always stay in character
- Tone must match personality
- Do not act neutral

User: {user_input}
"""

    response = llm.invoke(prompt)
    return response.content


# ------------------- WEATHER -------------------
def get_weather(city):
    api_key = os.getenv("WEATHERSTACK_API_KEY")
    url = f"http://api.weatherstack.com/current?access_key={api_key}&query={city}"

    response = requests.get(url).json()

    if "current" in response:
        temp = response["current"]["temperature"]
        desc = response["current"]["weather_descriptions"][0]
        return f"🌦 Weather in {city}: {temp}°C, {desc}"
    else:
        return "Weather not found"


# ------------------- SEARCH -------------------
def search_google(query):
    api_key = os.getenv("SERPAPI_API_KEY")

    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": api_key}

    response = requests.get(url, params=params).json()

    if "organic_results" in response:
        results = response["organic_results"][:3]
        output = "🔍 Top Results:\n"
        for r in results:
            output += f"- {r['title']}\n"
        return output
    else:
        return "No results found"


# ------------------- ROUTER -------------------
def process_input(user_input, personality):

    text = user_input.lower()

    if "weather" in text:
        city = user_input.split()[-1]
        return get_weather(city)

    elif "search" in text:
        query = user_input.replace("search", "")
        return search_google(query)

    else:
        return get_reply(user_input, personality)


# ------------------- BACKGROUND -------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------- SIDEBAR -------------------
st.sidebar.title("⚙️ Settings")

personality = st.sidebar.selectbox(
    "Choose Personality",
    ["Friendly", "Angry", "Teacher", "Flirty", "Sarcastic"]
)

if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.write("💡 Try:")
st.sidebar.write("- weather Mumbai")
st.sidebar.write("- search AI news")

# ------------------- MAIN -------------------
st.title("🤖 AI Assistant")

# Init memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat (ChatGPT style)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ------------------- INPUT FORM -------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("💬 Enter Message")
    submit = st.form_submit_button("Send")

if submit and user_input:

    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate reply
    reply = process_input(user_input, personality)

    # Save bot reply
    st.session_state.messages.append({"role": "assistant", "content": reply})

    st.rerun()