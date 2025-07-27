# tools/location_tool.py
from agents import function_tool
import requests
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# -------------------- 1. Get Location from IP --------------------
@function_tool
def get_location_from_ip() -> dict:
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        city = data.get("city", "Unknown City")
        country = data.get("country", "Unknown Country")
        loc = data.get("loc", "")
        if not loc:
            return {"error": "❌ Location coordinates not found in IP data."}

        latitude, longitude = loc.split(",")

        return {
            "city": city,
            "country": country,
            "latitude": latitude,
            "longitude": longitude,
            "description": f"📍 Your current location is **{city}, {country}**.\n🧭 Coordinates: Latitude **{latitude}**, Longitude **{longitude}**."
        }
    except Exception as e:
        return {"error": f"❌ Error retrieving location: {str(e)}"}




# -------------------- 2. Get Weather by Coordinates --------------------
@function_tool
def get_weather_from_location(latitude: str, longitude: str) -> str:
    """
    Get current weather for the given coordinates.
    """
    try:
        api_key = st.secrets["OPENWEATHERMAP_API_KEY"]

        if not api_key:
            return "❌ API key for OpenWeatherMap is missing. Set it in your .env file."

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
        )
        response = requests.get(url)
        data = response.json()

        if "weather" not in data or "main" not in data:
            return f"❌ Failed to get weather data. Response: {data}"

        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        city = data.get("name", "Unknown City")
        country = data.get("sys", {}).get("country", "Unknown Country")

        return f"🌤️ The current weather is **{weather}** with a temperature of **{temp}°C**."
    except Exception as e:
        return f"❌ Error retrieving weather: {str(e)}"


# -------------------- 3. Google Maps Nearby Search --------------------

@function_tool
def get_nearby_places_osm(lat, lon, radius=1000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    query = f"""
    [out:json];
    (
      node(around:{radius},{lat},{lon})[amenity];
      way(around:{radius},{lat},{lon})[amenity];
      relation(around:{radius},{lat},{lon})[amenity];
    );
    out center;
    """
    
    response = requests.get(overpass_url, params={'data': query})
    data = response.json()

    results = []
    for element in data['elements']:
        name = element['tags'].get('name', 'Unknown')
        amenity_type = element['tags'].get('amenity', 'N/A')
        lat = element.get('lat') or element.get('center', {}).get('lat')
        lon = element.get('lon') or element.get('center', {}).get('lon')
        results.append({
            'name': name,
            'type': amenity_type,
            'latitude': lat,
            'longitude': lon
        })

    return results 

   


# -------------------- 4. Real-Time Weather Alerts --------------------
@function_tool
def get_weather_alerts_from_location(latitude: str, longitude: str) -> str:
    """
    Get real-time weather alerts (like storms, heatwaves) for a given location.
    Returns user-friendly alert message or a safe status.
    """
    try:
        api_key = st.secrets["OPENWEATHERMAP_API_KEY"]

        if not api_key:
            return "❌ API key for OpenWeatherMap is missing. Set it in your .env file."

        url = (
            f"https://api.openweathermap.org/data/3.0/onecall?"
            f"lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
        )

        response = requests.get(url)
        data = response.json()

        alerts = data.get("alerts", [])
        if not alerts:
            return "✅ No active weather alerts for your area. You're safe! ☀️"

        alert_msgs = []
        for alert in alerts:
            event = alert.get("event", "Weather Alert")
            sender = alert.get("sender_name", "N/A")
            description = alert.get("description", "").strip().replace('\n', ' ')

            if len(description) > 300:
                description = description[:297] + "..."
                extra = " [Read more in the full alert.]"
            else:
                extra = ""

            alert_msgs.append(
                f"⚠️ **{event}** from *{sender}*\n📄 {description}{extra}\n📍 Location: {latitude}, {longitude}"
            )

        return "\n\n".join(alert_msgs)

    except Exception as e:
        return f"❌ Error retrieving weather alerts: {str(e)}"
