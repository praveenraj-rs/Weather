import streamlit as st
import requests
import time

# --------------------------
# Backend configuration
# --------------------------
BACKEND_URL = "http://localhost:8000/data"

# --------------------------
# Page setup
# --------------------------
st.set_page_config(page_title="ESP Weather Dashboard", layout="wide")

# Custom dark theme CSS
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

st.title("🌡️ ESP Weather Dashboard")

placeholder = st.empty()

# --------------------------
# Dashboard update loop
# --------------------------
while True:
    try:
        response = requests.get(BACKEND_URL)
        data = response.json() if response.status_code == 200 else {}

        with placeholder.container():
            st.subheader("Connected ESP Nodes")
            if not data:
                st.info("Waiting for ESP nodes to send data...")
            else:
                # Sort the node IDs numerically
                sorted_nodes = sorted(data.items(), key=lambda x: int(x[0]))

                cols = st.columns(len(sorted_nodes))
                for i, (node_id, node_data) in enumerate(sorted_nodes):
                    temp = node_data["temperature"]
                    hum = node_data["humidity"]

                    # Choose weather-like icons
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

        time.sleep(5)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        time.sleep(5)
