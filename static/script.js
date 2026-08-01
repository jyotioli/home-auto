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

  syncInitialStatus();
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
// --- FUNCTION TO SEND COMMANDS TO THE BACKEND ---
function sendCommand(device, state) {
  console.log(`Sending command: ${device} -> ${state}`);
  fetch(`/api/control/${device}/${state}`, {
    method: 'POST',
  })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data);

      if (data.status === 'success' && data.command) {
        updateUI(device, data.command);
      }
    })
    .catch(error => console.error('Error sending command:', error));
}

function syncInitialStatus() {
  fetch('/api/status')
    .then(response => response.json())
    .then(data => {
      if (data.status !== 'success' || !data.devices) return;

      Object.entries(data.devices).forEach(([device, state]) => {
        if (state && state !== 'UNKNOWN') {
          updateUI(device, state);
        }
      });
    })
    .catch(error => console.error('Error loading initial status:', error));
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