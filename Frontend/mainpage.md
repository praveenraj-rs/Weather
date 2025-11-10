@mainpage ESP Weather Dashboard

---

@section architecture System Architecture

The following diagram illustrates the overall data flow between firmware, backend, and frontend:

@dot
digraph ESP_Weather_Dashboard {
rankdir=LR;
node [shape=rectangle, style="rounded,filled", fillcolor="#3a3f5a", fontcolor="white", fontsize=11];
edge [color="#aaaaaa", arrowsize=0.9, penwidth=1.4];

    subgraph cluster_firmware {
        label="Firmware Layer (ESP Nodes)";
        color="#5c6bc0";
        style="rounded";
        fontcolor="white";
        fontsize=12;

        ESP32_Node [label="ESP32 Node\n(DHT Sensor)", fillcolor="#3949ab"];
        ESP8266_Node [label="ESP8266 Node\n(DHT Sensor)", fillcolor="#3949ab"];
    }

    subgraph cluster_backend {
        label="Backend Layer (FastAPI)";
        color="#43a047";
        style="rounded";
        fontcolor="white";
        fontsize=12;

        FastAPI_Server [label="FastAPI Server", fillcolor="#2e7d32"];
        JSON_Storage [label="Data Store", fillcolor="#4caf50"];
    }

    subgraph cluster_frontend {
        label="Frontend Layer (Streamlit)";
        color="#0277bd";
        style="rounded";
        fontcolor="white";
        fontsize=12;

        Streamlit_UI [label="Streamlit Dashboard", fillcolor="#0288d1"];
        User [label="User", shape=oval, fillcolor="#ab47bc"];
    }

    ESP32_Node -> FastAPI_Server [label="POST JSON"];
    ESP8266_Node -> FastAPI_Server [label="POST JSON"];
    FastAPI_Server -> JSON_Storage [label="Store Data"];
    JSON_Storage -> Streamlit_UI [label="GET /data"];
    Streamlit_UI -> User [label="Display Metrics"];

}
@enddot

@section overview Project Overview

**ESP Weather Dashboard** is a modern IoT monitoring system built using:

- **Streamlit (Frontend)** — for real-time data visualization
- **FastAPI (Backend)** — for data collection and REST API services
- **ESP32 / ESP8266 Nodes** — for temperature and humidity sensing

Each ESP node periodically sends JSON data to the FastAPI server.  
The Streamlit dashboard then displays these values live in an elegant **dark, weather-themed interface**.

---

@section tech Tech Stack

- **Firmware:** ESP32 / ESP8266 (Arduino)
- **Backend:** FastAPI (Python)
- **Frontend:** Streamlit (Python)
- **Libraries:** Requests, Pandas

---

@section setup Setup Instructions

**1️⃣ Clone the Repository**
@code{.bash}
git clone https://github.com/praveenraj-rs/Weather.git
cd esp-weather-dashboard
@endcode

**2️⃣ Install Dependencies**
@code{.bash}
pip install -r requirements.txt
@endcode
_(Requires Python 3.9 or newer)_

**3️⃣ Run the Backend (FastAPI)**
@code{.bash}
python3 Backend/backend.py
@endcode

**4️⃣ Run the Frontend (Streamlit)**
@code{.bash}
streamlit run Frontend/frontend.py --server.port 8501
@endcode

**5️⃣ Test Data Upload (via cURL)**
@code{.bash}
curl -X POST http://localhost:8000/update \
-H "Content-Type: application/json" \
-d '{"node_id":"1","temperature":26.5,"humidity":60.2}'
@endcode

---

@section features Features

Real-time temperature & humidity monitoring  
Auto-refresh every few seconds  
Interactive weather-themed dark UI  
Supports multiple ESP nodes  
Node sorting & data visualization  
Fully compatible with ESP32 and ESP8266 boards

---

@section structure Directory Structure

@code{.text}
├── Backend
│ ├── backend.py
│ ├── backend_update.py
│ ├── get_data.py
│ └── update_data.py
├── Frontend
│ ├── frontend.py
│ ├── frontend.sh
│ └── frontend_update.py
├── Firmware
│ ├── ESP32_Node
│ │ └── ESP32_Node.ino
│ └── ESP8266_Node
│ └── ESP8266_Node.ino
├── Documents
└── README.md
@endcode

---

@section firmware Example ESP Firmware Snippet

@code{.cpp}
String jsonData = "{\"node_id\": \"1\", \"temperature\": 25.6, \"humidity\": 61.2}";
http.begin("http://<server_ip>:8000/update");
http.addHeader("Content-Type", "application/json");
int code = http.POST(jsonData);
@endcode

---

GitHub: [https://github.com/praveenraj-rs/Weather.git](https://github.com/praveenraj-rs/Weather.git)
