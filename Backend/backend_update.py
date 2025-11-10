from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, List
from datetime import datetime

app = FastAPI()

# Allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing, make specific later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_store: Dict[str, Dict[str, float]] = {}
history_log: Dict[str, List[Dict[str, float]]] = {}

@app.post("/update")
def update_data(payload: Dict):
    node_id = str(payload["node_id"])
    temp = payload["temperature"]
    hum = payload["humidity"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data_store[node_id] = {
        "temperature": temp,
        "humidity": hum,
        "timestamp": timestamp,
    }

    # Save to history (for plotting)
    if node_id not in history_log:
        history_log[node_id] = []
    history_log[node_id].append({
        "time": timestamp,
        "temperature": temp,
        "humidity": hum
    })

    # Limit history length
    if len(history_log[node_id]) > 100:
        history_log[node_id].pop(0)

    return {"status": "success", "node_id": node_id}

@app.get("/data")
def get_data():
    return data_store

@app.get("/history/{node_id}")
def get_history(node_id: str):
    return history_log.get(node_id, [])


if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
