// CivicPulse login / sign-up page — talks to /api/auth.

const FETCH_OPTS = { credentials: "same-origin" };

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

async function postAuth(path, body) {
  const res = await fetch(path, {
    ...FETCH_OPTS,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data;
}

function goDashboard() {
  window.location.href = "dashboard.html";
}

// Redirect if already logged in.
fetch("/api/auth/me", FETCH_OPTS)
  .then((res) => res.json())
  .then((data) => {
    if (data.authenticated && data.user) goDashboard();
  })
  .catch(() => {});

document.getElementById("loginForm").addEventListener("submit", async (event) => {
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

  try {
    await postAuth("/api/auth/login", { email, password });
    goDashboard();
  } catch (err) {
    showError(
      "loginError",
      err.message || "Wrong email or password. New here? Create an account below."
    );
  }
});

document.getElementById("signupForm").addEventListener("submit", async (event) => {
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

  try {
    await postAuth("/api/auth/signup", { name, email, password });
    goDashboard();
  } catch (err) {
    showError("signupError", err.message || "Could not create account.");
  }
});

setMode("login");
