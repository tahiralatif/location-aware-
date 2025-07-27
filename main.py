from agents import Agent, OpenAIChatCompletionsModel , AsyncOpenAI ,Runner, RunConfig
# from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
from tools import get_location_from_ip, get_weather_from_location, get_nearby_places_osm, get_weather_alerts_from_location
import os
import chainlit as cl
import asyncio

load_dotenv()

@cl.on_chat_start
async def start_chat():
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
    MODEL_NAME= "gemini-1.5-flash"  

    extternal_clientt = AsyncOpenAI(
        api_key= API_KEY,
        base_url= "https://generativelanguage.googleapis.com/v1beta/openai/"       
    )

    model = OpenAIChatCompletionsModel(
        openai_client= extternal_clientt,
        model= MODEL_NAME,
    )

    config = RunConfig(
        model= model,
        model_provider= extternal_clientt,
        tracing_disabled= True,
    )

    agent = Agent(
        name= "CitySense",
        instructions = """
You are a helpful assistant specialized in location-based services.

Your capabilities include:
- Detecting user location using IP.
- Providing real-time weather conditions.
- Showing nearby places (using OpenStreetMap).
- Giving weather alerts like storms or heatwaves.

Strictly follow these rules:
1. Only respond to location-based or weather-related queries.
2. If the query is unrelated (e.g. history, jokes, random coding), politely refuse and guide the user back to location tools.
3. For every location task, if coordinates are missing, first call `get_location_from_ip`.
4. If the user asks about nearby amenities (restaurants, hospitals, etc.), use `get_nearby_places_osm`.
5. When showing alerts, always call `get_weather_alerts_from_location` after confirming location.
6. Keep all responses short, structured, and include emoji-based feedback (✅, ❌, ⚠️ etc.).
7. Do not hallucinate locations. Always use tool responses for output.

Only rely on tool functions for any location, weather, or nearby place data.

""",
        tools=[get_location_from_ip, get_weather_from_location, get_nearby_places_osm, get_weather_alerts_from_location],
    )

    # 🧠 Save into memory session
    cl.user_session.set("agent", agent)
    cl.user_session.set("history", [])
    cl.user_session.set("run_config", config)

    await cl.Message("👋 Welcome to **CitySense**!\n I can help you find your location, show the weather, and find nearby places like clinics or restaurants").send()
   


@cl.on_message
async def main(message: cl.Message):    
    msg = await cl.Message(content="⏳ Processing your request...").send()

    # 🧠 Retrieve from session using correct key names
    agent = cl.user_session.get("agent")
    history = cl.user_session.get("history")
    config = cl.user_session.get("run_config")

    history.append({"role": "user", "content": message.content})

    result = Runner.run_sync(
        starting_agent= agent,
        input = history,
        run_config= config,
    )

    
    msg.content = result.final_output
    await msg.update()

    # 🧠 
    cl.user_session.set("history", result.to_input_list())
    print("Result Final Output:", result.final_output)



