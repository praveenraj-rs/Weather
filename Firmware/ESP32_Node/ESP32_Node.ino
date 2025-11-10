#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// -----------------------------
// DHT Sensor Configuration
// -----------------------------
#define DHTPIN 4         // GPIO4 (D4) — adjust if needed
#define DHTTYPE DHT11    // or DHT22
DHT dht(DHTPIN, DHTTYPE);

// -----------------------------
// WiFi & Server Config
// -----------------------------
const char* ssid = "ESS";
const char* password = "12345678";
const char* serverName = "http://192.168.131.95:8000/update";

const char* node_id = "1";  // Change for each ESP node (e.g. "2", "3")

// -----------------------------
// Setup
// -----------------------------
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\n✅ Connected to WiFi!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  dht.begin();
}

// -----------------------------
// Main Loop
// -----------------------------
void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();

    if (isnan(temp) || isnan(hum)) {
      Serial.println("❌ Failed to read from DHT sensor!");
      delay(2000);
      return;
    }

    HTTPClient http;
    WiFiClient client;

    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/json");

    // Build JSON payload
    String jsonData = "{\"node_id\": \"" + String(node_id) + 
                      "\", \"temperature\": " + String(temp, 2) + 
                      ", \"humidity\": " + String(hum, 2) + "}";

    int httpResponseCode = http.POST(jsonData);

    Serial.print("📡 Sent Data -> ");
    Serial.println(jsonData);
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);

    http.end();
  } else {
    Serial.println("⚠️ WiFi Disconnected! Reconnecting...");
    WiFi.begin(ssid, password);
  }

  delay(5000);  // Send data every 5 seconds
}
