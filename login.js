// CivicPulse login / sign-up page.
//
// Demo-only auth: accounts live in localStorage until a backend
// /api/auth endpoint exists. Do not reuse a real password here —
// passwords are stored in plain text in this browser.

const ACCOUNTS_KEY = "civicpulse_accounts";
const SESSION_KEY = "civicpulse_session";

function loadAccounts() {
  try {
    return JSON.parse(localStorage.getItem(ACCOUNTS_KEY)) || [];
  } catch {
    return [];
  }
}

function saveAccounts(accounts) {
  localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(accounts));
}

function startSession(account) {
  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify({ name: account.name, email: account.email })
  );
  window.location.href = "dashboard.html";
}

// ── mode toggle ─────────────────────────────────────────

let mode = "login";

function setMode(next) {
  mode = next;
  const login = mode === "login";
  document.getElementById("loginForm").hidden = !login;
  document.getElementById("signupForm").hidden = login;
  document.getElementById("loginTitle").textContent = login
    ? "Welcome back"
    : "Create your account";
  document.getElementById("loginSub").textContent = login
    ? "Log in to your CivicPulse account."
    : "Join CivicPulse to report and track issues in your city.";
  document.getElementById("toggleText").textContent = login
    ? "New to CivicPulse?"
    : "Already have an account?";
  document.getElementById("toggleMode").textContent = login
    ? "Create an account"
    : "Log in";
  showError("loginError", null);
  showError("signupError", null);
}

document.getElementById("toggleMode").addEventListener("click", () => {
  setMode(mode === "login" ? "signup" : "login");
});

// ── validation helpers ──────────────────────────────────

function showError(id, message) {
  const el = document.getElementById(id);
  el.hidden = !message;
  el.textContent = message || "";
}

function normalizeEmail(email) {
  return email.trim().toLowerCase();
}

function isValidEmail(email) {
  const probe = document.createElement("input");
  probe.type = "email";
  probe.value = email;
  return email !== "" && probe.checkValidity();
}

// ── log in ──────────────────────────────────────────────

document.getElementById("loginForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const email = normalizeEmail(document.getElementById("loginEmail").value);
  const password = document.getElementById("loginPassword").value;

  if (!isValidEmail(email)) {
    showError("loginError", "Enter a valid email address.");
    return;
  }
  if (!password) {
    showError("loginError", "Enter your password.");
    return;
  }

  const account = loadAccounts().find((a) => a.email === email);
  if (!account || account.password !== password) {
    showError("loginError", "Wrong email or password. New here? Create an account below.");
    return;
  }

  startSession(account);
});

// ── create account ──────────────────────────────────────

document.getElementById("signupForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const name = document.getElementById("signupName").value.trim();
  const email = normalizeEmail(document.getElementById("signupEmail").value);
  const password = document.getElementById("signupPassword").value;
  const confirm = document.getElementById("signupConfirm").value;

  if (!name) {
    showError("signupError", "Enter your name.");
    return;
  }
  if (!isValidEmail(email)) {
    showError("signupError", "Enter a valid email address.");
    return;
  }
  if (password.length < 6) {
    showError("signupError", "Password must be at least 6 characters.");
    return;
  }
  if (password !== confirm) {
    showError("signupError", "Passwords don't match.");
    return;
  }

  const accounts = loadAccounts();
  if (accounts.some((a) => a.email === email)) {
    showError("signupError", "An account with that email already exists — log in instead.");
    return;
  }

  const account = { name, email, password };
  accounts.push(account);
  saveAccounts(accounts);
  startSession(account);
});

setMode("login");
