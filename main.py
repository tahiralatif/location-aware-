from agents import Agent, OpenAIChatCompletionsModel , AsyncOpenAI ,Runner, RunConfig
from dotenv import load_dotenv
from tools import get_location_from_ip, get_weather_from_location, get_nearby_places_osm, get_weather_alerts_from_location
import os
import asyncio
load_dotenv()


async def main():
    

    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
    MODEL_NAME= "gemini-2.0-flash"  

    # step 1 creat provider ----------
    extternal_clientt = AsyncOpenAI(
        api_key= API_KEY,
        base_url= "https://generativelanguage.googleapis.com/v1beta/openai/"       
    )

    # step 2 create model ----------
    model = OpenAIChatCompletionsModel(
        openai_client= extternal_clientt,
        model= MODEL_NAME,
    
    )


    config =  RunConfig(
        model= model,
        model_provider= extternal_clientt,
        tracing_disabled= True,

    )

    triage_Agent = Agent(
        name= "Location-Aware AI Assistant",
        instructions = """
You are CitySense — a smart, location-aware AI assistant.

Your core task is to:
1. Detect the user's current location.
2. Fetch real-time weather information based on that location.
3. Find nearby essential places such as clinics, restaurants, or user-specified services.
4. Alert the user if any real-time weather warnings or alerts exist for their area.

You must:
- Use the available tools *only when required*.
- Combine the location, weather, alerts (if any), and nearby places into a **clear, concise, and user-friendly response**.
- Make sure your answers are structured, helpful, and use simple, human-like language.
- Default to Celsius for temperature unless otherwise specified.
- Ask follow-up questions only when needed (e.g., when radius or category of places is unclear).
""",
        tools=[get_location_from_ip, get_weather_from_location , get_nearby_places_osm, get_weather_alerts_from_location],
      
    )

    result = await Runner.run(
        starting_agent= triage_Agent,
        input = "What's my location, what's the weather, and show me nearby clinic.",
        run_config= config
    )

    answer = result.final_output
    print(f"Answer : \n {answer}")  




if __name__ == "__main__":
    asyncio.run(main())
