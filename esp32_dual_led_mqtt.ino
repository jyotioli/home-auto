#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

// Wokwi uses this public Wi-Fi network by default.
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// HiveMQ Cloud MQTT broker details from your Flask app.
const char* mqtt_server = "9c65ea2f2186455482b55de00023441d.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_user = "esp32_homeautomation";
const char* mqtt_pass = "Jyotioli@19";

// GPIO pins connected to the LEDs.
constexpr uint8_t LIGHT_PIN = 18;
constexpr uint8_t FAN_PIN = 19;

// MQTT topics used by the Flask app.
#define LIGHT_STATUS_TOPIC  "home/light/status"
#define LIGHT_COMMAND_TOPIC "home/light/set"
#define FAN_STATUS_TOPIC    "home/fan/status"
#define FAN_COMMAND_TOPIC   "home/fan/set"

WiFiClientSecure secureClient;
PubSubClient mqttClient(secureClient);

void setDeviceState(uint8_t pin, const String& state) {
  bool isOn = state.equalsIgnoreCase("ON");
  digitalWrite(pin, isOn ? HIGH : LOW);
}

void publishDeviceState(const char* statusTopic, uint8_t pin, const String& state) {
  setDeviceState(pin, state);
  mqttClient.publish(statusTopic, state.c_str(), true);
}

void connectToWiFi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  message.trim();
  message.toUpperCase();

  Serial.printf("Message on topic: %s -> %s\n", topic, message.c_str());

  if (String(topic) == LIGHT_COMMAND_TOPIC) {
    if (message == "ON" || message == "OFF") {
      publishDeviceState(LIGHT_STATUS_TOPIC, LIGHT_PIN, message);
    }
  } else if (String(topic) == FAN_COMMAND_TOPIC) {
    if (message == "ON" || message == "OFF") {
      publishDeviceState(FAN_STATUS_TOPIC, FAN_PIN, message);
    }
  }
}

bool reconnectMQTT() {
  if (mqttClient.connected()) {
    return true;
  }

  Serial.print("Attempting MQTT connection...");
  String clientId = "ESP32Client-";
  clientId += String(random(0xffff), HEX);

  if (mqttClient.connect(clientId.c_str(), mqtt_user, mqtt_pass)) {
    Serial.println("connected!");
    mqttClient.subscribe(LIGHT_COMMAND_TOPIC);
    mqttClient.subscribe(FAN_COMMAND_TOPIC);

    // Publish initial OFF states so the app sees a known value.
    publishDeviceState(LIGHT_STATUS_TOPIC, LIGHT_PIN, "OFF");
    publishDeviceState(FAN_STATUS_TOPIC, FAN_PIN, "OFF");
    return true;
  }

  Serial.printf("failed, rc=%d. Retrying in 5s\n", mqttClient.state());
  return false;
}

void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(0));

  pinMode(LIGHT_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  digitalWrite(LIGHT_PIN, LOW);
  digitalWrite(FAN_PIN, LOW);

  connectToWiFi();

  secureClient.setInsecure();
  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(callback);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }

  if (!mqttClient.connected()) {
    reconnectMQTT();
  }

  mqttClient.loop();
  delay(10);
}
