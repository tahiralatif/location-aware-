# 📍 CitySense – Real-Time Location & Weather Companion 🌦️

CitySense is your smart AI-powered assistant that gives you real-time **weather updates**, **location-based services**, **nearby places**, and **live weather alerts** — all in one clean and beautiful UI.

## 🚀 Features

- 🌍 Detects your **location via IP**
- 🌤️ Displays **real-time weather**
- 🏥 Shows **nearby amenities** like hospitals, cafes, schools
- ⚠️ Fetches **real-time weather alerts**
- ✨ Clean UI with animations and dark mode styling

## 🛠️ Tech Stack

- Python 🐍
- Streamlit 📺
- OpenAI Agents + Gemini API
- OpenWeatherMap API
- Overpass (OSM)

## 🧠 How It Works

CitySense uses agent-based reasoning and tool integration with Gemini API to dynamically:
- Detect the user's IP location
- Call OpenWeatherMap for real-time weather & alerts
- Use Overpass API to find nearby amenities

## 🧪 Example Queries

- "What's the weather like here?"
- "Nearby hospitals"
- "Any storm alerts?"

## 📦 Setup

1. Clone this repo
2. Create `.env` file with:
```
GEMINI_API_KEY=your_google_gemini_api_key
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run with:
```bash
streamlit run main.py
```

## 🏆 Hackathon Ready

- ⏱️ Runs in under 5 minutes
- 📦 Clean project structure
- 📄 Polished README

Built for the Boot.dev Hackathon 🎉

---
Made with 💙 by Tahira Rajput
