# ESP32 Circuit Setup For Two LEDs

This setup keeps your frontend and MQTT topics unchanged.

## What to place in Wokwi or on a breadboard

- 1 x ESP32 Dev Board
- 2 x LEDs
- 2 x 220 ohm resistors
- Jumper wires

## Wiring

- LED 1 anode to GPIO 18 through a 220 ohm resistor
- LED 1 cathode to GND
- LED 2 anode to GPIO 19 through a 220 ohm resistor
- LED 2 cathode to GND
- ESP32 GND must be shared with both LEDs

## MQTT Topic Mapping

- `home/light/set` controls LED 1
- `home/light/status` reports LED 1 state
- `home/fan/set` controls LED 2
- `home/fan/status` reports LED 2 state

## Upload Notes

- Open the sketch in Arduino IDE or PlatformIO.
- Install the `WiFi` and `PubSubClient` libraries.
- Replace `YOUR_WIFI_SSID` and `YOUR_WIFI_PASSWORD` with your actual Wi-Fi credentials.
- Upload the sketch to the ESP32.
- Open the Serial Monitor at 115200 baud to watch the connection status.

## Important Notes

- Do not use a relay for this version.
- Keep the frontend as-is. The second button still says fan, but it now drives the second LED.
- If you want more stable behavior on real hardware, keep the ESP32 on GPIO 18 and GPIO 19.
