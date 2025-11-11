import requests
import json

# URL of your FastAPI backend
url = "http://10.11.129.142:8000/data"

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("📡 Data received from backend:\n")
        print(json.dumps(data, indent=4))
    else:
        print(f"⚠️ Error {response.status_code}: {response.text}")
except requests.exceptions.RequestException as e:
    print("❌ Failed to connect to server:", e)
