// Simple authentication utilities using localStorage

function saveAuthentication(username, remember) {
  localStorage.setItem('loggedInUser', username);
  if (remember) localStorage.setItem('rememberMe', 'true');
  else localStorage.removeItem('rememberMe');
}

function isUserAuthenticated() {
  return !!localStorage.getItem('loggedInUser');
}

function getCurrentUser() {
  return localStorage.getItem('loggedInUser') || 'Guest';
}

function redirectToDashboard() {
  window.location.href = '/'; // Change to this
}

function redirectToLogin() {
  window.location.href = 'LOGIN.HTML';
}

function protectPage() {
  if (!isUserAuthenticated()) {
    redirectToLogin();
    return false;
  }
  return true;
}

function logout() {
  localStorage.removeItem('loggedInUser');
  localStorage.removeItem('rememberMe');
  localStorage.removeItem('rememberedUser');
  localStorage.removeItem('rememberedPass');
  redirectToLogin();
}