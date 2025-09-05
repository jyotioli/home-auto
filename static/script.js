document.addEventListener('DOMContentLoaded', () => {
  if (!protectPage()) return;

  document.getElementById('currentUser').textContent = getCurrentUser();

  const toggles = [
    { btn: 'lightToggle', status: 'lightStatus', icon: 'lightIcon' },
    { btn: 'fanToggle', status: 'fanStatus', icon: 'fanIcon' }
  ];

  toggles.forEach(({ btn, status, icon }) => {
    const button = document.getElementById(btn);
    button.addEventListener('click', () => {
      const statusElem = document.getElementById(status);
      const iconElem = document.getElementById(icon);
      const isOn = statusElem.textContent === 'ON';

      statusElem.textContent = isOn ? 'OFF' : 'ON';
      button.querySelector('.btn-text').textContent = isOn ? 'OFF' : 'ON';

      statusElem.style.color = isOn ? 'red' : 'green';
      iconElem.style.color = isOn ? 'gray' : 'orange';

      // You can integrate HTTPS request to ESP32 here for real control
    });
  });

  updateTime();
});

function updateTime() {
  const currentTimeElem = document.getElementById('currentTime');
  if (!currentTimeElem) return;
  setInterval(() => {
    const now = new Date();
    currentTimeElem.textContent = now.toLocaleTimeString();
  }, 1000);
}
// --- SETUP SOCKET.IO CONNECTION ---
const socket = io("http://127.0.0.1:5000");

socket.on('connect', () => {
  console.log('✅ Connected to backend server via WebSocket');
});

// --- HANDLE REAL-TIME STATUS UPDATES FROM SERVER ---
socket.on('status_update', (data) => {
  console.log('Received status update:', data);
  const { device, payload } = data; // e.g., device='light', payload='ON'
  updateUI(device, payload);
});

// --- ADD CLICK LISTENERS TO BUTTONS ---
document.getElementById('lightToggle').addEventListener('click', () => {
  const currentState = document.getElementById('lightStatus').textContent;
  const newState = currentState === 'ON' ? 'OFF' : 'ON';
  sendCommand('light', newState);
});

document.getElementById('fanToggle').addEventListener('click', () => {
  const currentState = document.getElementById('fanStatus').textContent;
  const newState = currentState === 'ON' ? 'OFF' : 'ON';
  sendCommand('fan', newState);
});


// --- FUNCTION TO SEND COMMANDS TO THE BACKEND ---
function sendCommand(device, state) {
  console.log(`Sending command: ${device} -> ${state}`);
  fetch(`/api/control/${device}/${state}`, {
    method: 'POST',
  })
    .then(response => response.json())
    .then(data => console.log('Server response:', data))
    .catch(error => console.error('Error sending command:', error));
}

// --- FUNCTION TO UPDATE THE UI BASED ON DEVICE STATUS ---
function updateUI(device, status) {
  const isON = status === 'ON';
  const statusElem = document.getElementById(`${device}Status`);
  const button = document.getElementById(`${device}Toggle`);
  const iconElem = document.getElementById(`${device}Icon`);

  if (statusElem) {
    statusElem.textContent = status;
    statusElem.style.color = isON ? 'green' : 'red';
  }
  if (button) {
    button.querySelector('.btn-text').textContent = status;
  }
  if (iconElem) {
    const activeColor = device === 'light' ? 'orange' : '#007BFF';
    iconElem.style.color = isON ? activeColor : 'gray';
  }
}

// Keep the time updated
function updateTime() {
  const currentTimeElem = document.getElementById('currentTime');
  if (!currentTimeElem) return;
  setInterval(() => {
    const now = new Date();
    currentTimeElem.textContent = now.toLocaleTimeString();
  }, 1000);
}
updateTime(); // Run the function