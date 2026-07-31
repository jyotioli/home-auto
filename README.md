# 🏠 Smart Home Automation Dashboard

A full-stack IoT home automation system that lets you control real appliances (light, fan) remotely through a web dashboard — built end-to-end from hardware to cloud.

🔗 **Live Demo:** https://smarthome-dashboard-4b1r.onrender.com
📦 **Tech Stack:** ESP32 · MQTT (TLS) · HiveMQ Cloud · Flask · JavaScript · HTML/CSS

## What it does
This project implements a full hardware-to-cloud IoT pipeline — ESP32 firmware, MQTT (TLS) over HiveMQ Cloud, Flask backend, live dashboard. The physical layer is currently demonstrated via Wokwi circuit simulation (running the actual firmware) since I don't have hardware on hand right now — the cloud pipeline, backend, and dashboard are fully live and real.

## How it works
1. **ESP32** runs firmware that connects to WiFi and subscribes to MQTT topics over a secure TLS connection.
2. **HiveMQ Cloud** acts as the MQTT broker, relaying commands between the web dashboard and the physical device.
3. **Flask backend** serves the dashboard and publishes MQTT messages when a user toggles a switch.
4. **Frontend (HTML/CSS/JS)** gives a clean UI to control the light and fan, with live status updates.

## Features
- Real-time device control over secure MQTT (TLS on port 8883)
- Live status sync between physical device and dashboard (works even if toggled from either side)
- Deployed and publicly accessible (not just localhost)

## Tech Details
- **Hardware:** ESP32, relay modules for light/fan control
- **Protocol:** MQTT over TLS via HiveMQ Cloud
- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Render

## Setup
Environment variables required (not committed to repo):
- `MQTT_SERVER`
- `MQTT_USER`
- `MQTT_PASSWORD`

## Live URL
👉 https://smarthome-dashboard-4b1r.onrender.com
