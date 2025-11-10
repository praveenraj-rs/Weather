## @file frontend.py
#  @brief Streamlit-based IoT dashboard for ESP sensor data and OpenWeather API.
#  @details
#  This Streamlit frontend visualizes live environmental data collected from ESP-based IoT nodes
#  and integrates real-time weather information using the OpenWeather API.
#  The dashboard displays:
#   - Temperature, humidity, and status from multiple ESP devices
#   - Live weather data for a selected city
#   - Local date and time display
#   - A GitHub footer link for project reference
#
#  The application automatically refreshes every 5 seconds to ensure real-time updates.
#
#  @author
#  Anuli Jenn T
#  @date
#  2025-11-11
#  @version
#  2.0

import streamlit as st
import requests
import time
from datetime import datetime

# --------------------------
# Configuration
# --------------------------

## @brief Backend API endpoint for ESP sensor data.
BACKEND_URL = "http://localhost:8000/data"

## @brief Base URL for OpenWeather public API.
OPENWEATHER_API = "https://openweathermap.org/data/2.5/weather"

## @brief Demo API key for OpenWeather API.
#  @note Replace with your own API key for full functionality.
OPENWEATHER_KEY = "439d4b804bc8187953eb36d2a8c26a02"


# --------------------------
# Streamlit page setup
# --------------------------
## @brief Configure Streamlit application layout and appearance.
st.set_page_config(page_title="ESP + Weather Dashboard", layout="wide")

## @brief Apply custom dark-themed CSS styling for the dashboard.
st.markdown(
    """
    <style>
    body {
        background: radial-gradient(circle at 20% 20%, #1e1e2f, #111);
        color: #fff;
    }
    .main {
        background-color: transparent;
        color: #fff;
    }
    h1, h2, h3, h4, h5 {
        color: #f8f8f8 !important;
    }
    .weather-box, .ow-box {
        background: linear-gradient(135deg, rgba(40,40,60,0.9), rgba(20,20,30,0.9));
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .weather-box:hover, .ow-box:hover {
        transform: scale(1.03);
        box-shadow: 0 8px 30px rgba(0,0,0,0.6);
    }
    .emoji {
        font-size: 2.5rem;
        display: block;
        margin-bottom: 0.5rem;
    }
    footer {
        text-align: center;
        margin-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌦️ ESP Weather Dashboard")


# --------------------------
# City input for OpenWeather
# --------------------------
## @brief User input field to select a city for OpenWeather data.
city = st.text_input("🌍 Enter city name:", "Ettimadai").strip()

## @brief Streamlit placeholder for dynamic dashboard updates.
placeholder = st.empty()


# --------------------------
# Helper Functions
# --------------------------

def fetch_openweather_data(city):
    """!
    @brief Fetch current weather data from OpenWeather API.
    @param city City name as string.
    @return dict: Parsed JSON response containing temperature, humidity, wind, and description.
    """
    try:
        ow_url = f"{OPENWEATHER_API}?q={city}&appid={OPENWEATHER_KEY}&units=metric"
        response = requests.get(ow_url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to fetch OpenWeather data.")
            return {}
    except Exception as e:
        st.error(f"Error fetching weather: {e}")
        return {}


def fetch_esp_data():
    """!
    @brief Retrieve environmental data from backend ESP nodes.
    @return dict: Node-wise dictionary containing temperature, humidity, and timestamps.
    """
    try:
        response = requests.get(BACKEND_URL)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        st.error(f"Error fetching ESP data: {e}")
        return {}


def get_weather_emoji(temp, hum):
    """!
    @brief Determine weather emoji based on temperature and humidity.
    @param temp Temperature in °C.
    @param hum Humidity percentage.
    @return str: Unicode emoji string.
    """
    if temp > 30:
        emoji = "☀️"
    elif temp > 20:
        emoji = "⛅"
    elif temp > 10:
        emoji = "🌧️"
    else:
        emoji = "❄️"

    if hum > 80:
        emoji += " 💧"
    elif hum < 30:
        emoji += " 🔥"

    return emoji


def render_footer():
    """!
    @brief Display the GitHub project footer with hover animation and SVG icon.
    """
    st.markdown(
        """
        <footer style="text-align:center; margin-top:2rem;">
            <a href="https://github.com/praveenraj-rs/esp-weather-dashboard"
            target="_blank"
            style="text-decoration:none; display:inline-flex; align-items:center; gap:8px;
                    color:#ccc; font-weight:500; transition:color 0.3s ease;">
                <svg xmlns="http://www.w3.org/2000/svg" 
                    width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 .5C5.65.5.5 5.65.5 12a11.5 11.5 0 007.87 10.93c.58.1.79-.25.79-.55v-1.93
                    c-3.2.7-3.88-1.54-3.88-1.54-.53-1.34-1.3-1.7-1.3-1.7-1.06-.72.08-.7.08-.7
                    1.17.08 1.78 1.2 1.78 1.2 1.04 1.78 2.73 1.26 3.4.97.1-.76.4-1.27.73-1.56
                    -2.55-.29-5.23-1.28-5.23-5.67 0-1.25.44-2.27 1.17-3.07-.12-.29-.51-1.46.11-3.05
                    0 0 .96-.31 3.15 1.17a10.9 10.9 0 015.73 0c2.18-1.48 3.14-1.17 3.14-1.17
                    .62 1.59.23 2.76.11 3.05.73.8 1.16 1.82 1.16 3.07 0 4.4-2.69 5.37-5.25 5.65
                    .41.35.78 1.03.78 2.08v3.09c0 .3.2.66.8.55A11.5 11.5 0 0023.5 12C23.5 5.65
                    18.35.5 12 .5z"/>
                </svg>
                <span>View this project on GitHub</span>
            </a>
            <style>
                footer a:hover {
                    color: #58a6ff !important;
                    transform: scale(1.05);
                }
                footer svg {
                    transition: transform 0.3s ease, color 0.3s ease;
                }
                footer a:hover svg {
                    transform: rotate(10deg) scale(1.2);
                    color: #58a6ff;
                }
            </style>
        </footer>
        """,
        unsafe_allow_html=True
    )


# --------------------------
# Main Execution Loop
# --------------------------
## @brief Continuous dashboard update loop.
#  @details Refreshes every 5 seconds to fetch and render updated weather and ESP data.
while True:
    with placeholder.container():
        cols_top = st.columns([3, 2])

        # ---- Left: OpenWeather Data ----
        with cols_top[0]:
            ow_data = fetch_openweather_data(city)
            if ow_data:
                temp = ow_data["main"]["temp"]
                hum = ow_data["main"]["humidity"]
                wind = ow_data["wind"]["speed"]
                desc = ow_data["weather"][0]["description"].capitalize()
                icon = ow_data["weather"][0]["icon"]

                st.markdown(
                    f"""
                    <div class="ow-box">
                        <h2>🌍 Weather in {city.title()}</h2>
                        <img src="https://openweathermap.org/img/wn/{icon}@2x.png" width="80">
                        <h1>{temp:.1f}°C</h1>
                        <h3>{desc}</h3>
                        <p>💧 Humidity: {hum}%</p>
                        <p>🌬️ Wind: {wind} m/s</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # ---- Right: Date and Time ----
        with cols_top[1]:
            now = datetime.now()
            st.markdown(
                f"""
                <div class="ow-box">
                    <h2>🕒 {now.strftime("%I:%M %p")}</h2>
                    <h3>{now.strftime("%A, %d %B %Y")}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ---- ESP Node Data ----
        st.subheader("Connected ESP Nodes")
        esp_data = fetch_esp_data()
        if not esp_data:
            st.info("Waiting for ESP nodes to send data...")
        else:
            sorted_nodes = sorted(esp_data.items(), key=lambda x: int(x[0]))
            cols = st.columns(len(sorted_nodes))
            for i, (node_id, node_data) in enumerate(sorted_nodes):
                temp = node_data["temperature"]
                hum = node_data["humidity"]
                timestamp = node_data.get("timestamp", "N/A")
                emoji = get_weather_emoji(temp, hum)

                with cols[i]:
                    st.markdown(
                        f"""
                        <div class="weather-box">
                            <span class="emoji">{emoji}</span>
                            <h3>Node {node_id}</h3>
                            <h4>{temp:.1f}°C</h4>
                            <p>💧 {hum:.1f}% Humidity</p>
                            <small>Last update:<br>{timestamp}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # ---- Footer ----
        render_footer()

    time.sleep(5)
