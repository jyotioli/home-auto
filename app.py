import os
#new comment
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt


MQTT_BROKER_URL = os.getenv(
    "MQTT_BROKER_URL",
    "9c65ea2f2186455482b55de00023441d.s1.eu.hivemq.cloud",
)
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "hivemq.webclient.1785583878328")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "a2ml9xDb;0qX!1?T,MAV")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))

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

try:
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[MQTT] on_connect fired, reason_code={reason_code}")
    reason_value = getattr(reason_code, "value", reason_code)
    if reason_value == 0:
        print("[MQTT] Connected to broker successfully")
        # Replace with your actual topics:
        client.subscribe(TOPIC_LIGHT_STATUS)
        client.subscribe(TOPIC_FAN_STATUS)
    else:
        print(f"[MQTT] Connection FAILED, reason_code={reason_code}")

def on_disconnect(client, userdata, reason_code, properties=None, *args):
    print(f"[MQTT] Disconnected! reason_code={reason_code}")

def on_log(client, userdata, level, buf):
    print(f"[MQTT LOG] {buf}")

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


def publish_device_state(device, state):
    state = state.upper()
   
    if not mqtt_client.is_connected():
        return False, "MQTT client not connected to broker (check server logs)"
    if device == "light":
        topic = TOPIC_LIGHT_COMMAND
    elif device == "fan":
        topic = TOPIC_FAN_COMMAND
    else:
        return False, "Invalid device"

    if state not in {"ON", "OFF"}:
        return False, "Invalid state"

    result = mqtt_client.publish(topic, state)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        return False, f"MQTT publish failed with code {result.rc}"

    return True, state


@socketio.on("connect")
def handle_connect():
    for device, state in device_states.items():
        if state != "UNKNOWN":
            emit("status_update", {"device": device, "payload": state})


@app.route("/")
def dashboard_page():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("LOGIN.HTML")


@app.route("/LOGIN.HTML")
def legacy_login_page():
    return render_template("LOGIN.HTML")


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


def configure_mqtt_client():
    # 1. Important: Tell Paho to use WebSockets
    global mqtt_client # Ensure we are modifying the global client object if needed by your setup
    
    try:
        # Re-initialize the client specifically for WebSockets
        mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
    except AttributeError:
        mqtt_client = mqtt.Client(transport="websockets")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message # Keep your existing message handler
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_log = on_log
   
    
    # 2. Set the secure path for HiveMQ WebSockets
    mqtt_client.ws_set_options(path="/mqtt") 
    
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.tls_set() # Still required for secure WebSockets (wss://)
    
    # 3. Connect using Port 8884
    # Ensure your MQTT_PORT variable is set to 8884 in Render's Environment settings, 
    # or hardcode it here for testing:
    mqtt_client.connect_async(MQTT_BROKER_URL, 8884, 60) 
    
    mqtt_client.loop_start()

configure_mqtt_client() # this step help me to connect to render

if __name__ == "__main__":
   # configure_mqtt_client()
    print("Starting Smart Home Server at http://127.0.0.1:5000/")
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)