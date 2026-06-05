# 🏠 Home Automation System

Control home appliances remotely via a web dashboard using 
IoT hardware and cloud messaging.

## Demo


## What it does
- Control fan and light from any browser, anywhere in the world
- Real-time state sync using MQTT over TLS
- Runs on ESP32 microcontroller with cloud broker

## Tech Stack
| Layer | Technology |
|---|---|
| Hardware | ESP32 microcontroller |
| Messaging | MQTT over TLS (HiveMQ Cloud) |
| Backend | Python Flask |
| Frontend | HTML, CSS, Vanilla JavaScript |

## Architecture
Browser → Flask API → HiveMQ Cloud Broker → ESP32 → Appliance

## Setup
1. Clone the repo
2. Copy `.env.example` to `.env` and fill your credentials
3. Install Python deps: `pip install flask paho-mqtt`
4. Flash ESP32 firmware (see /firmware folder)
5. Run: `python app.py`

## What I learned
- MQTT protocol and TLS security
- Hardware-software integration
- Real-time bidirectional communication
- Cloud broker configuration

## Environment Variables
See `.env.example` — never commit real credentials
