# home-auto
this is your esp32 code 
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

// --- UPDATE WITH YOUR DETAILS ---
const char* ssid = "realme"; //add ur wifi
const char* password = "12345678"; //add password
// Double-check this line for any typos
const char* mqtt_server = "9c65ea2f2186455482b55de00023441d.s1.eu.hivemq.cloud"; //user from hivemq
const int mqtt_port = 8883; // Use 8883 for secure TLS
const char* mqtt_user = "esp32_homeautomation"; //name
const char* mqtt_pass = "Jyotioli@19"; //hivemq pass

// --- PIN DEFINITIONS ---
const int lightPin = 2; // Built-in LED or a relay for a real light
const int fanPin = 4;   // Another GPIO pin for a fan relay

// --- MQTT TOPICS ---
#define LIGHT_STATUS_TOPIC "home/light/status"
#define LIGHT_COMMAND_TOPIC "home/light/set"
#define FAN_STATUS_TOPIC "home/fan/status"
#define FAN_COMMAND_TOPIC "home/fan/set"

WiFiClientSecure espClientSecure;
PubSubClient client(espClientSecure);

void setup_wifi() {
    delay(10);
    Serial.println("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected!");
}

void callback(char* topic, byte* payload, unsigned int length) {
    String message;
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    Serial.printf("Message on topic: %s -> %s\n", topic, message.c_str());

    if (String(topic) == LIGHT_COMMAND_TOPIC) {
        if (message == "ON") {
            digitalWrite(lightPin, HIGH);
            client.publish(LIGHT_STATUS_TOPIC, "ON", true);
        } else if (message == "OFF") {
            digitalWrite(lightPin, LOW);
            client.publish(LIGHT_STATUS_TOPIC, "OFF", true);
        }
    } else if (String(topic) == FAN_COMMAND_TOPIC) {
        if (message == "ON") {
            digitalWrite(fanPin, HIGH);
            client.publish(FAN_STATUS_TOPIC, "ON", true);
        } else if (message == "OFF") {
            digitalWrite(fanPin, LOW);
            client.publish(FAN_STATUS_TOPIC, "OFF", true);
        }
    }
}

void reconnect() {
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        if (client.connect("ESP32_SmartHome", mqtt_user, mqtt_pass)) {
            Serial.println("connected!");
            client.subscribe(LIGHT_COMMAND_TOPIC);
            client.subscribe(FAN_COMMAND_TOPIC);
            // Publish initial states on reconnect
            client.publish(LIGHT_STATUS_TOPIC, "OFF", true);
            client.publish(FAN_STATUS_TOPIC, "OFF", true);
        } else {
            Serial.printf(" failed, rc=%d. Retrying in 5s\n", client.state());
            delay(5000);
        }
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(lightPin, OUTPUT);
    pinMode(fanPin, OUTPUT);
    digitalWrite(lightPin, LOW);
    digitalWrite(fanPin, LOW);
    
    // For ESP32, you might need to provide root CA cert for TLS
    // espClientSecure.setCACert(root_ca); // See documentation if needed
    
    setup_wifi();
    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(callback);
}

void loop() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();
}
