import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt



# --- CONFIGURATION (UPDATE WITH YOUR DETAILS) ---
MQTT_BROKER_URL = "9c65ea2f2186455482b55de00023441d.s1.eu.hivemq.cloud"
MQTT_USERNAME = "esp32_homeautomation"
MQTT_PASSWORD = "Jyotioli@19"
MQTT_PORT = 8883

VALID_CREDENTIALS = [
    {'username': 'admin', 'password': 'admin123'},
    {'username': 'user', 'password': 'user123'},
    {'username': 'smarthome', 'password': 'home2025'}
]

# --- STATE STORAGE ---
# Dictionary to store the last known state of each device
device_states = {
    'light': 'UNKNOWN',
    'fan': 'UNKNOWN'
}

# --- FLASK, SOCKETIO, MQTT SETUP ---
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Create MQTT client (compatible with both paho-mqtt v1.x and v2.x)
try:
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    mqtt_client = mqtt.Client()


def on_connect(client, userdata, flags, reason_code, properties=None):
    ...

    if reason_code == 0:
        print("✅ Connected to MQTT Broker!")
        client.subscribe("home/light/status")
        client.subscribe("home/fan/status")
    else:
        print(f"❌ Failed to connect to MQTT, reason code {reason_code}")

def on_message(client, userdata, msg):
    try:
        device = msg.topic.split('/')[1]
        payload = msg.payload.decode()
        
        # Update the server's state storage
        if device in device_states:
            device_states[device] = payload
            print(f"📩 State Updated: {device} -> {payload}")
            
        # Forward the update to all connected web clients
        socketio.emit('status_update', {'device': device, 'payload': payload})
    except Exception as e:
        print(f"Error in on_message: {e}")

# --- NEW: Send initial states to a newly connected client ---
@socketio.on('connect')
def handle_connect():
    print(f"✅ Web client connected. Sending initial states: {device_states}")
    for device, state in device_states.items():
        if state != 'UNKNOWN':
            emit('status_update', {'device': device, 'payload': state})

# --- MQTT CONNECTION ---
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.tls_set()
mqtt_client.connect(MQTT_BROKER_URL, MQTT_PORT, 60)
mqtt_client.loop_start()

# --- WEB PAGE & API ROUTES (Unchanged) ---
@app.route('/LOGIN')
def login_page():
    return render_template('LOGIN.HTML')

@app.route('/')
def dashboard_page():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if any(u['username'] == username and u['password'] == password for u in VALID_CREDENTIALS):
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/control/<string:device>/<string:state>', methods=['POST'])
def control_device(device, state):
    if device not in ['light', 'fan'] or state.upper() not in ['ON', 'OFF']:
        return jsonify({"status": "error", "message": "Invalid device or state"}), 400
    topic = f"home/{device}/set"
    payload = state.upper()
    print(f"🚀 Publishing to MQTT: {topic} -> {payload}")
    mqtt_client.publish(topic, payload)
    return jsonify({"status": "success", "command": payload})

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    print("🌍 Starting Smart Home Server. Open your browser to http://127.0.0.1:5000/login")
from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt

# --- CONFIGURATION (UPDATE WITH YOUR DETAILS) ---
MQTT_BROKER_URL = "9c65ea2f2186455482b55de00023441d.s1.eu.hivemq.cloud"
MQTT_USERNAME = "esp32_homeautomation"
MQTT_PASSWORD = "Jyotioli@19"
MQTT_PORT = 8883

VALID_CREDENTIALS = [
    {'username': 'admin', 'password': 'admin123'},
    {'username': 'user', 'password': 'user123'},
    {'username': 'smarthome', 'password': 'home2025'}
]

# --- STATE STORAGE ---
# Dictionary to store the last known state of each device
device_states = {
    'light': 'UNKNOWN',
    'fan': 'UNKNOWN'
}

# --- FLASK, SOCKETIO, MQTT SETUP ---
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected with result code {reason_code}")

def on_message(client, userdata, message):
    print(f"Received message: {message.topic} -> {message.payload}")

def on_message(client, userdata, msg):
    try:
        device = msg.topic.split('/')[1]
        payload = msg.payload.decode()
        
        # Update the server's state storage
        if device in device_states:
            device_states[device] = payload
            print(f"📩 State Updated: {device} -> {payload}")
            
        # Forward the update to all connected web clients
        socketio.emit('status_update', {'device': device, 'payload': payload})
    except Exception as e:
        print(f"Error in on_message: {e}")

# --- NEW: Send initial states to a newly connected client ---
@socketio.on('connect')
def handle_connect():
    print(f"✅ Web client connected. Sending initial states: {device_states}")
    for device, state in device_states.items():
        if state != 'UNKNOWN':
            emit('status_update', {'device': device, 'payload': state})

# --- MQTT CONNECTION ---
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.tls_set()
mqtt_client.connect(MQTT_BROKER_URL, MQTT_PORT, 60)
mqtt_client.loop_start()

# --- WEB PAGE & API ROUTES (Unchanged) ---
@app.route('/login')
def login_page():
    return render_template('LOGIN.HTML')

@app.route('/')
def dashboard_page():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if any(u['username'] == username and u['password'] == password for u in VALID_CREDENTIALS):
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/control/<string:device>/<string:state>', methods=['POST'])
def control_device(device, state):
    if device not in ['light', 'fan'] or state.upper() not in ['ON', 'OFF']:
        return jsonify({"status": "error", "message": "Invalid device or state"}), 400
    topic = f"home/{device}/set"
    payload = state.upper()
    print(f"🚀 Publishing to MQTT: {topic} -> {payload}")
    mqtt_client.publish(topic, payload)
    return jsonify({"status": "success", "command": payload})

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    print("🌍 Starting Smart Home Server. Open your browser to http://127.0.0.1:5000/login")
    socketio.run(app, host="0.0.0.0", port=5000)