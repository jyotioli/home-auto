import os
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt

# -----------------------------
# Environment config
# -----------------------------
MQTT_BROKER_URL = os.getenv("MQTT_BROKER_URL", "")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8884"))  # 8884 for WSS on HiveMQ Cloud

TOPIC_LIGHT_COMMAND = "home/light/set"
TOPIC_LIGHT_STATUS = "home/light/status"
TOPIC_FAN_COMMAND = "home/fan/set"
TOPIC_FAN_STATUS = "home/fan/status"

VALID_CREDENTIALS = [
    {"username": "admin", "password": "admin123"},
    {"username": "user", "password": "user123"},
    {"username": "smarthome", "password": "home2025"},
]

device_states = {"light": "UNKNOWN", "fan": "UNKNOWN"}

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

mqtt_client = None  # initialize later


# -----------------------------
# MQTT callbacks
# -----------------------------
def on_connect(client, userdata, flags, reason_code, properties=None):
    reason_value = getattr(reason_code, "value", reason_code)
    if reason_value == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe(TOPIC_LIGHT_STATUS)
        client.subscribe(TOPIC_FAN_STATUS)
        print(f"Subscribed to: {TOPIC_LIGHT_STATUS}, {TOPIC_FAN_STATUS}")
    else:
        print(f"❌ MQTT connection failed with reason code: {reason_code}")


def on_message(client, userdata, msg):
    try:
        device = msg.topic.split("/")[1]
        payload = msg.payload.decode().strip().upper()

        if device in device_states:
            device_states[device] = payload
            print(f"State updated: {device} -> {payload}")

        socketio.emit("status_update", {"device": device, "payload": payload})
    except Exception as exc:
        print(f"MQTT message handling error: {exc}")


# -----------------------------
# MQTT helpers
# -----------------------------
def publish_device_state(device, state):
    global mqtt_client
    state = state.upper()

    if device == "light":
        topic = TOPIC_LIGHT_COMMAND
    elif device == "fan":
        topic = TOPIC_FAN_COMMAND
    else:
        return False, "Invalid device"

    if state not in {"ON", "OFF"}:
        return False, "Invalid state"

    if mqtt_client is None:
        return False, "MQTT client not initialized"

    result = mqtt_client.publish(topic, state)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        return False, f"MQTT publish failed with code {result.rc}"

    return True, state


def configure_mqtt_client():
    global mqtt_client

    if not MQTT_BROKER_URL or not MQTT_USERNAME or not MQTT_PASSWORD:
        print("⚠️ MQTT env vars missing. Set MQTT_BROKER_URL, MQTT_USERNAME, MQTT_PASSWORD")
        return

    try:
        mqtt_client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            transport="websockets",
        )
    except AttributeError:
        mqtt_client = mqtt.Client(transport="websockets")

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # HiveMQ Cloud secure websocket path
    mqtt_client.ws_set_options(path="/mqtt")
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.tls_set()  # required for wss://

    print(f"Connecting MQTT to {MQTT_BROKER_URL}:{MQTT_PORT} via WSS...")
    mqtt_client.connect_async(MQTT_BROKER_URL, MQTT_PORT, 60)
    mqtt_client.loop_start()


# -----------------------------
# Socket.IO events
# -----------------------------
@socketio.on("connect")
def handle_connect():
    for device, state in device_states.items():
        if state != "UNKNOWN":
            emit("status_update", {"device": device, "payload": state})


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def dashboard_page():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/LOGIN.HTML")
def legacy_login_page():
    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def handle_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    is_valid = any(
        account["username"] == username and account["password"] == password
        for account in VALID_CREDENTIALS
    )
    if is_valid:
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({"status": "success", "devices": device_states}), 200


@app.route("/api/control/<string:device>/<string:state>", methods=["POST"])
def control_device(device, state):
    success, result = publish_device_state(device, state)
    if not success:
        return jsonify({"status": "error", "message": result}), 400

    print(f"Published {device} -> {result}")
    return jsonify({"status": "success", "command": result}), 200


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    configure_mqtt_client()
    port = int(os.getenv("PORT", "5000"))  # Render provides PORT
    print(f"Starting Smart Home Server on 0.0.0.0:{port}")
    socketio.run(app, host="0.0.0.0", port=port)