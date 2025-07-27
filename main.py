import streamlit as st
from streamlit_lottie import st_lottie
import requests
from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI, Runner, RunConfig
from tools import (
    get_location_from_ip,
    get_weather_from_location,
    get_nearby_places_osm,
    get_weather_alerts_from_location,
)
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

# ============ Utils ============ #
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def animated_title():
    st.title("📍 CitySense")
    st.markdown("### Your Real-Time Location & Weather Companion 🌤️")
    st.markdown("Enter a query below (like **'What's the weather?'** or **'Nearby hospitals'**)")

# ============ Load Animations ============ #
location_lottie = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_iwmd6pyr.json")
weather_lottie = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_Stt1R6.json")
places_lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_fcfjwiyb.json")
alert_lottie = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_t24tpvcu.json")

# ============ Streamlit UI ============ #
st.set_page_config(page_title="CitySense", page_icon="📍", layout="centered")

# --- Custom Styling with Background Color ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0F172A !important;
        color: #F1F5F9;
        font-family: 'Segoe UI', sans-serif;
    }
    .stTextInput > div > div > input {
        background-color: #1E293B;
        color: #F8FAFC;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #334155;
    }
    .stButton > button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
        border: none;
    }
    .stMarkdown {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.3);
    }
    h1, h2, h3 {
        color: #60A5FA;
    }
    </style>
""", unsafe_allow_html=True)


with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        animated_title()
    with col2:
        st_lottie(location_lottie, height=150, key="location")

query = st.text_input("💬 Ask me something location-based:")

# ============ Agent Initialization ============ #
if "agent" not in st.session_state:
    API_KEY = st.secrets["GEMINI_API_KEY"]

    if not API_KEY:
        st.error("❌ GEMINI_API_KEY not found in .env")
    else:
        external_client = AsyncOpenAI(
            api_key=API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        model = OpenAIChatCompletionsModel(
            openai_client=external_client,
            model="gemini-2.0-flash"
        )

        config = RunConfig(
            model=model,
            model_provider=external_client,
            tracing_disabled=True,
        )

        agent = Agent(
            name="CitySense",
            instructions="""
You are a helpful assistant specialized in location-based services.

Capabilities:
- Detect IP-based location
- Get weather 🌦️
- Find nearby places 🏥
- Show real-time weather alerts ⚠️

Rules:
1. Don't hallucinate — only use tool responses
2. Add emojis for every result
3. Respond short and clearly
4. If coordinates missing, call get_location_from_ip
""",
            tools=[
                get_location_from_ip,
                get_weather_from_location,
                get_nearby_places_osm,
                get_weather_alerts_from_location,
            ],
        )

        st.session_state.agent = agent
        st.session_state.config = config
        st.session_state.history = []

# ============ On Submit ============ #
if query and "agent" in st.session_state:
    st.session_state.history.append({"role": "user", "content": query})
    with st.spinner("⏳ Thinking..."):
        result = asyncio.run(Runner.run(
            starting_agent=st.session_state.agent,
            input=st.session_state.history,
            run_config=st.session_state.config,
        ))

    st.success("✅ Here’s what I found:")
    st.markdown(result.final_output)

    # 🎉 Animations Based on Query Type
    if "weather" in query.lower():
        st_lottie(weather_lottie, height=200)
    elif "nearby" in query.lower() or "restaurant" in query.lower() or "hospital" in query.lower():
        st_lottie(places_lottie, height=200)
    elif "alert" in query.lower() or "storm" in query.lower():
        st_lottie(alert_lottie, height=200)

    st.session_state.history = result.to_input_list()
