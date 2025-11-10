#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

#define DHTPIN D4       // GPIO2 for DHT
#define DHTTYPE DHT11   // or DHT22
DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "ESS";
const char* password = "12345678";
const char* serverName = "http://192.168.131.95:8000/update";

const char* node_id = "1"; // Change for each ESP node (e.g., "2", "3")

void setup() {
  Serial.begin(9600);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  dht.begin();
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();

    if (isnan(temp) || isnan(hum)) {
      Serial.println("Failed to read from DHT sensor!");
      delay(2000);
      return;
    }

    WiFiClient client;
    HTTPClient http;

    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{\"node_id\": \"" + String(node_id) + "\", \"temperature\": " + String(temp) + ", \"humidity\": " + String(hum) + "}";
    
    int httpResponseCode = http.POST(jsonData);
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);

    http.end();
  } else {
    Serial.println("WiFi disconnected");
  }

  delay(5000); // send every 5s
}
