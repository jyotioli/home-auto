const ESP32_IP = '192.168.1.100';
const BYPASS_ESP32_CHECK = true;

const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const passwordToggle = document.getElementById('passwordToggle');
const loginBtn = document.getElementById('loginBtn');
const loginSpinner = document.getElementById('loginSpinner');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const connectionStatus = document.getElementById('connectionStatus');
const connectionText = document.getElementById('connectionText');
const rememberMeCheckbox = document.getElementById('rememberMe');

const VALID_CREDENTIALS = [
  { username: 'admin', password: 'admin123' },
  { username: 'user', password: 'user123' },
  { username: 'smarthome', password: 'home2025' }
];

document.addEventListener('DOMContentLoaded', () => {
  if (isUserAuthenticated()) {
    redirectToDashboard();
    return;
  }
  loadRememberedCredentials();
  checkESP32Connection();
  setupEventListeners();
});

function setupEventListeners() {
  if (loginForm) {
    loginForm.addEventListener('submit', handleLogin);
  }
  if (passwordToggle) {
    passwordToggle.addEventListener('click', togglePasswordVisibility);
  }
  document.addEventListener('keypress', e => {
    if (e.key === 'Enter' && !loginBtn.disabled) handleLogin(e);
  });
  if (usernameInput) usernameInput.addEventListener('input', clearError);
  if (passwordInput) passwordInput.addEventListener('input', clearError);
}

async function handleLogin(e) {
    e.preventDefault();

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!username || !password) {
        showError('Please enter both username and password');
        return;
    }

    setLoadingState(true);

    try {
        // Send login request to the backend server
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            // If login is successful
            saveAuthentication(username, rememberMeCheckbox.checked);
            showSuccess('Login successful! Redirecting...');
            setTimeout(() => redirectToDashboard(), 1500);
        } else {
            // If backend returns an error (e.g., 401 Unauthorized)
            showError('Invalid username or password');
            setLoadingState(false);
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Cannot connect to the server. Please try again.');
        setLoadingState(false);
    }
}

// Keep all your other helper functions:
// togglePasswordVisibility, showError, showSuccess,
// clearError, setLoadingState, etc.
// The content of AUTH.JS does not need to change.

async function checkESP32Connection() {
  const esp32Url = fetch('https://${ESP32_IP}/ping');

  if (BYPASS_ESP32_CHECK) {
    connectionStatus.className = 'status-indicator connected';
    connectionText.textContent = 'ESP32 Bypassed (Testing Mode)';
    return true;
  }
  try {
    const response = await fetch(esp32Url, { method: 'GET', mode: 'cors' });
    if (response.ok) {
      connectionStatus.className = 'status-indicator connected';
      connectionText.textContent = 'ESP32 Connected';
      return true;
    } else {
      connectionStatus.className = 'status-indicator disconnected';
      connectionText.textContent = 'ESP32 Disconnected';
      return false;
    }
  } catch {
    connectionStatus.className = 'status-indicator disconnected';
    connectionText.textContent = 'ESP32 Disconnected';
    return false;
  }
}

function togglePasswordVisibility() {
  const type = passwordInput.type === 'password' ? 'text' : 'password';
  passwordInput.type = type;

  const icon = passwordToggle.querySelector('i');
  icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
}

function showError(msg) {
  errorText.textContent = msg;
  errorMessage.style.display = 'flex';
  errorMessage.classList.add('shake');
  setTimeout(() => errorMessage.classList.remove('shake'), 500);
}

function showSuccess(msg) {
  errorMessage.style.display = 'flex';
  errorMessage.style.background = 'rgba(34, 197, 94, 0.1)';
  errorMessage.style.borderColor = 'rgba(34, 197, 94, 0.2)';
  errorMessage.style.color = '#22c55e';
  errorText.textContent = msg;

  const icon = errorMessage.querySelector('i');
  if (icon) icon.className = 'fas fa-check-circle';
}

function clearError() {
  errorMessage.style.display = 'none';
  errorMessage.style.background = 'rgba(239, 68, 68, 0.1)';
  errorMessage.style.borderColor = 'rgba(239, 68, 68, 0.2)';
  errorMessage.style.color = '#ef4444';

  const icon = errorMessage.querySelector('i');
  if (icon) icon.className = 'fas fa-exclamation-circle';
}

function setLoadingState(isLoading) {
  loginBtn.disabled = isLoading;
  const btnText = document.querySelector('.btn-text');
  if (isLoading) {
    if (btnText) btnText.style.display = 'none';
    if (loginSpinner) loginSpinner.style.display = 'inline-block';
  } else {
    if (btnText) btnText.style.display = 'inline';
    if (loginSpinner) loginSpinner.style.display = 'none';
  }
}

function loadRememberedCredentials() {
  if (localStorage.getItem('rememberMe') === 'true') {
    usernameInput.value = localStorage.getItem('rememberedUser') || '';
    passwordInput.value = localStorage.getItem('rememberedPass') || '';
    rememberMeCheckbox.checked = true;
  }
}

function saveAuthentication(username, remember) {
  localStorage.setItem('loggedInUser', username);
  if (remember) {
    localStorage.setItem('rememberMe', 'true');
    localStorage.setItem('rememberedUser', username);
    localStorage.setItem('rememberedPass', passwordInput.value);
  } else {
    localStorage.removeItem('rememberMe');
    localStorage.removeItem('rememberedUser');
    localStorage.removeItem('rememberedPass');
  }
}
// In LOGIN.JS, replace the old handleLogin function
// The rest of your LOGIN.JS file can remain the same

document.addEventListener('DOMContentLoaded', () => {
    if (isUserAuthenticated()) {
        redirectToDashboard();
        return;
    }
    // Any other setup functions you have
    setupEventListeners();
});

function setupEventListeners() {
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    if (passwordToggle) {
        passwordToggle.addEventListener('click', togglePasswordVisibility);
    }
    // Add other listeners as needed
}

