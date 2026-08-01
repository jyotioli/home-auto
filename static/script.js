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
      const currentState = statusElem.textContent.trim().toUpperCase();
      const newState = currentState === 'ON' ? 'OFF' : 'ON';

      sendCommand(btn.replace('Toggle', ''), newState);
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
const socket = io();

socket.on('connect', () => {
  console.log('✅ Connected to backend server via WebSocket');
});

// --- HANDLE REAL-TIME STATUS UPDATES FROM SERVER ---
socket.on('status_update', (data) => {
  console.log('Received status update:', data);
  const { device, payload } = data; // e.g., device='light', payload='ON'
  updateUI(device, payload);
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