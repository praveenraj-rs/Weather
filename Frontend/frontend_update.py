import streamlit as st
import requests
import pandas as pd
import time

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="ESP Weather Dashboard", layout="wide")

# --- CSS (dark theme) ---
st.markdown("""
<style>
body {background: radial-gradient(circle at 20% 20%, #1e1e2f, #111); color: #fff;}
.weather-box {
    background: linear-gradient(135deg, rgba(40,40,60,0.9), rgba(20,20,30,0.9));
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.weather-box:hover {transform: scale(1.02); box-shadow: 0 8px 30px rgba(0,0,0,0.6);}
.emoji {font-size: 2.2rem; display: block; margin-bottom: 0.4rem;}
.small-muted {color: #bfc9d9; font-size: 12px;}
</style>
""", unsafe_allow_html=True)

st.title("🌡️ ESP Weather Dashboard")

# ensure session state for selected node
if "selected_node" not in st.session_state:
    st.session_state.selected_node = "None"

# sidebar selection (kept, with unique key)
st.sidebar.markdown("## 📡 Node Controls")
st.sidebar.write("Click a node's button to view history, or choose below.")
# placeholder for active nodes; updated each loop
active_nodes_placeholder = st.sidebar.empty()
selected_from_sidebar = st.sidebar.selectbox("Select node (sidebar)", options=["None"], key="sidebar_select")

# main placeholder for dynamic content
placeholder = st.empty()

POLL_INTERVAL = 5  # seconds

# Use a simple refresh loop (keeps behaviour like before)
while True:
    try:
        res = requests.get(f"{BACKEND_URL}/data", timeout=5)
        data = res.json() if res.status_code == 200 else {}

        # update sidebar active nodes selectbox choices
        node_ids_sorted = []
        if data:
            node_ids_sorted = [n for n, _ in sorted(data.items(), key=lambda x: int(x[0]))]
        active_nodes_placeholder.write("Active Nodes: " + (", ".join(node_ids_sorted) if node_ids_sorted else "None"))

        # If user chose from sidebar selectbox, update session_state
        if selected_from_sidebar != "None":
            st.session_state.selected_node = selected_from_sidebar

        with placeholder.container():
            st.subheader("Connected ESP Nodes")

            if not data:
                st.info("Waiting for ESP nodes to send data...")
            else:
                # Sort nodes numerically
                sorted_nodes = sorted(data.items(), key=lambda x: int(x[0]))

                # create columns, but limit max columns per row to keep layout tidy
                max_cols = 4
                # chunk nodes into rows of max_cols
                rows = [sorted_nodes[i:i+max_cols] for i in range(0, len(sorted_nodes), max_cols)]

                for row in rows:
                    cols = st.columns(len(row))
                    for col, (node_id, node_data) in zip(cols, row):
                        temp = node_data["temperature"]
                        hum = node_data["humidity"]

                        # Weather emoji logic
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

                        # Unique button key per node (prefixed)
                        btn_key = f"btn_{node_id}"

                        with col:
                            # show node card
                            st.markdown(f"""
                                <div class="weather-box">
                                    <span class="emoji">{emoji}</span>
                                    <h3>Node {node_id}</h3>
                                    <h4>{temp:.1f}°C</h4>
                                    <p>💧 {hum:.1f}% Humidity</p>
                                    <div class="small-muted">Last: {node_data.get('timestamp','-')}</div>
                                </div>
                                """, unsafe_allow_html=True)

                            # button to view node history. unique key ensures no duplicate-key error.
                            if st.button(f"View Node {node_id}", key=btn_key):
                                st.session_state.selected_node = node_id
                                # optional: scroll to charts area by re-rendering (Streamlit will re-run)
                                # we set selected_node and break to allow charts to show on same run.
                                # break

            # Show history charts for selected node (if any)
            sel = st.session_state.selected_node
            if sel != "None":
                st.markdown(f"### 📊 Node {sel} - Historical Data")
                hist_res = requests.get(f"{BACKEND_URL}/history/{sel}")
                if hist_res.status_code == 200 and hist_res.json():
                    df = pd.DataFrame(hist_res.json())
                    if not df.empty:
                        df["time"] = pd.to_datetime(df["time"])
                        df = df.sort_values("time")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.line_chart(df.set_index("time")["temperature"])
                        with col2:
                            st.line_chart(df.set_index("time")["humidity"])
                    else:
                        st.info("No historical data yet for this node.")
                else:
                    st.info("No historical data yet for this node.")

        # sleep before next poll
        time.sleep(POLL_INTERVAL)

    except requests.exceptions.RequestException as exc:
        # network/backend error
        placeholder.error(f"Error fetching data: {exc}")
        time.sleep(POLL_INTERVAL)
    except Exception as e:
        placeholder.error(f"Unexpected error: {e}")
        time.sleep(POLL_INTERVAL)
