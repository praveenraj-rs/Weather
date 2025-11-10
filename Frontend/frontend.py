## @file frontend.py
#  @brief Streamlit frontend dashboard for ESP Weather Monitoring System.
#  @details
#  This Streamlit application continuously fetches weather data from the backend REST API
#  and displays live temperature and humidity readings from multiple ESP nodes.
#
#  It uses a custom dark UI theme, dynamic weather icons, and auto-refresh functionality
#  to provide a user-friendly IoT dashboard.
#
#  @author
#  Praveenraj R S
#  @date
#  2025-11-11
#  @version
#  1.0

import streamlit as st
import requests
import time

# --------------------------
# Backend configuration
# --------------------------
## @brief URL endpoint of the backend API.
## @details The frontend fetches JSON data periodically from this URL.
BACKEND_URL = "http://localhost:8000/data"


# --------------------------
# Page setup
# --------------------------
## @brief Configure Streamlit page layout and appearance.
st.set_page_config(page_title="ESP Weather Dashboard", layout="wide")

## @brief Custom dark theme CSS for dashboard styling.
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
    h1, h2, h3, h4 {
        color: #f8f8f8 !important;
    }
    .stMetric label {
        color: #ccc !important;
    }
    .weather-box {
        background: linear-gradient(135deg, rgba(40,40,60,0.9), rgba(20,20,30,0.9));
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .weather-box:hover {
        transform: scale(1.03);
        box-shadow: 0 8px 30px rgba(0,0,0,0.6);
    }
    .emoji {
        font-size: 2.5rem;
        display: block;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

## @brief Main dashboard title.
st.title("🌡️ ESP Weather Dashboard")

## @brief Placeholder for dynamic dashboard updates.
placeholder = st.empty()


# --------------------------
# Functions
# --------------------------
def fetch_backend_data():
    """!
    @brief Fetch JSON weather data from the backend API.
    @return dict: Parsed JSON data from the server if successful, otherwise empty dictionary.
    """
    try:
        response = requests.get(BACKEND_URL)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return {}


def get_weather_emoji(temp, hum):
    """!
    @brief Determine a weather emoji based on temperature and humidity.
    @param temp Temperature in Celsius.
    @param hum Humidity in percentage.
    @return str: Emoji string representing the current weather condition.
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


def render_dashboard(data):
    """!
    @brief Render weather cards for all connected ESP nodes.
    @param data Dictionary containing node data with temperature, humidity, and timestamp.
    """
    with placeholder.container():
        st.subheader("Connected ESP Nodes")

        if not data:
            st.info("Waiting for ESP nodes to send data...")
            return

        # Sort node IDs numerically
        sorted_nodes = sorted(data.items(), key=lambda x: int(x[0]))
        cols = st.columns(len(sorted_nodes))

        for i, (node_id, node_data) in enumerate(sorted_nodes):
            temp = node_data["temperature"]
            hum = node_data["humidity"]
            emoji = get_weather_emoji(temp, hum)

            with cols[i]:
                st.markdown(
                    f"""
                    <div class="weather-box">
                        <span class="emoji">{emoji}</span>
                        <h3>Node {node_id}</h3>
                        <h4>{temp:.1f}°C</h4>
                        <p>💧 {hum:.1f}% Humidity</p>
                        <small>Last update:<br>{node_data['timestamp']}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# --------------------------
# Main Execution Loop
# --------------------------
## @brief Continuously update the dashboard every 5 seconds with backend data.
while True:
    data = fetch_backend_data()
    render_dashboard(data)
    time.sleep(5)
