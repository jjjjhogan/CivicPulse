// CivicPulse resident issue report form.
//
// Submitted reports POST to /api/reports (SQLite Signal rows, source=resident).
// Falls back to localStorage only if the server is unreachable.

const STORAGE_KEY = "civicpulse_resident_reports";

// Reportable issue types — derived from CATEGORY_KEYWORDS (signals-data.js)
// so the report form can't drift from the dashboard's category list.
const ISSUE_CATEGORIES = Object.keys(CATEGORY_KEYWORDS);

const IRVINE_CENTER = [33.6846, -117.8265];
// Rough bounding box around Irvine used to bias/limit geocoding results.
const IRVINE_VIEWBOX = "-117.92,33.59,-117.68,33.77";

const selectedTags = new Set();
let picked = null; // { lat, lng }
let pickerMap;
let pinMarker;

// ── tag pills ───────────────────────────────────────────

const tagContainer = document.getElementById("issueTags");
for (const category of ISSUE_CATEGORIES) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tag-filter";
  const dot = document.createElement("span");
  dot.className = "tag-dot";
  // CATEGORY_COLORS comes from signals-data.js (loaded by report.html).
  dot.style.background = CATEGORY_COLORS[category] || "#666";
  btn.append(dot, category.replaceAll("_", " "));
  btn.addEventListener("click", () => {
    if (selectedTags.has(category)) {
      selectedTags.delete(category);
      btn.classList.remove("selected");
    } else {
      selectedTags.add(category);
      btn.classList.add("selected");
    }
  });
  tagContainer.appendChild(btn);
}

// ── picker map ──────────────────────────────────────────

function setPin(lat, lng, zoomTo = false) {
  picked = { lat, lng };
  if (!pinMarker) {
    pinMarker = L.marker([lat, lng], { draggable: true }).addTo(pickerMap);
    pinMarker.on("dragend", () => {
      const pos = pinMarker.getLatLng();
      picked = { lat: pos.lat, lng: pos.lng };
      setGeoStatus(`Pin set at ${pos.lat.toFixed(4)}, ${pos.lng.toFixed(4)} — drag to adjust.`);
    });
  } else {
    pinMarker.setLatLng([lat, lng]);
  }
  if (zoomTo) pickerMap.setView([lat, lng], 15);
}

function setGeoStatus(text, isError = false) {
  const el = document.getElementById("geoStatus");
  el.textContent = text;
  el.style.color = isError ? "#b04a3a" : "";
}

pickerMap = L.map("pickerMap", { scrollWheelZoom: false }).setView(IRVINE_CENTER, 12);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(pickerMap);

pickerMap.on("click", (event) => {
  setPin(event.latlng.lat, event.latlng.lng);
  setGeoStatus(
    `Pin set at ${event.latlng.lat.toFixed(4)}, ${event.latlng.lng.toFixed(4)} — drag to adjust.`
  );
});

// ── geocoding (OpenStreetMap Nominatim) ─────────────────

async function geocodeAddress() {
  const input = document.getElementById("fieldAddress");
  const query = input.value.trim();
  if (!query) {
    setGeoStatus("Type an address first, then click “Find on map”.", true);
    input.focus();
    return;
  }

  const btn = document.getElementById("locateBtn");
  btn.disabled = true;
  setGeoStatus("Looking up address…");

  try {
    const url =
      "https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1" +
      `&viewbox=${IRVINE_VIEWBOX}&bounded=0&q=${encodeURIComponent(query)}`;
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`Geocoder returned ${res.status}`);
    const results = await res.json();
    if (results.length === 0) {
      setGeoStatus("Address not found — try adding “Irvine, CA”, or click the map instead.", true);
      return;
    }
    const { lat, lon, display_name } = results[0];
    setPin(parseFloat(lat), parseFloat(lon), true);
    setGeoStatus(`Found: ${display_name}`);
  } catch {
    setGeoStatus("Address lookup failed — click the map to drop a pin instead.", true);
  } finally {
    btn.disabled = false;
  }
}

document.getElementById("locateBtn").addEventListener("click", geocodeAddress);
document.getElementById("fieldAddress").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    geocodeAddress();
  }
});

// ── validation + submit ─────────────────────────────────

function showError(message, field) {
  const el = document.getElementById("formError");
  el.textContent = message;
  el.hidden = false;
  if (field) {
    field.classList.add("invalid");
    field.focus();
  }
}

function clearErrors() {
  document.getElementById("formError").hidden = true;
  for (const el of document.querySelectorAll(".invalid")) el.classList.remove("invalid");
}

function loadLocalReports() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveReportLocally(report) {
  const reports = loadLocalReports();
  reports.unshift(report);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(reports));
}

async function saveReport(report) {
  let res;
  try {
    res = await fetch("/api/reports", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify(report),
    });
  } catch {
    saveReportLocally(report);
    console.warn("Saved report locally; server unreachable.");
    return { signal: report, storage: "local" };
  }

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || `Server returned ${res.status}`);
  }
  return res.json();
}

document.getElementById("reportForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  clearErrors();

  const name = document.getElementById("fieldName");
  const email = document.getElementById("fieldEmail");
  const title = document.getElementById("fieldTitle");
  const submitBtn = document.getElementById("submitBtn");

  if (!name.value.trim()) return showError("Please enter your name.", name);
  if (!email.value.trim() || !email.checkValidity())
    return showError("Please enter a valid email address.", email);
  if (!title.value.trim()) return showError("Please give the issue a short title.", title);
  if (selectedTags.size === 0)
    return showError("Please select at least one issue type.");
  if (!document.getElementById("fieldAddress").value.trim())
    return showError("Please enter the address of the issue.", document.getElementById("fieldAddress"));
  if (!picked)
    return showError("Please locate the issue on the map (“Find on map” or click the map).");

  // CivicSignal-shaped record (scrapers/schema.py)
  const report = {
    source: "resident",
    outlet: "Resident report",
    title: title.value.trim(),
    body: document.getElementById("fieldBody").value.trim(),
    url: "",
    categories: [...selectedTags],
    published_utc: new Date().toISOString().slice(0, 10),
    metadata: {
      lat: picked.lat,
      lng: picked.lng,
      address: document.getElementById("fieldAddress").value.trim(),
      reporter_name: name.value.trim(),
      reporter_email: email.value.trim(),
      reporter_phone: document.getElementById("fieldPhone").value.trim(),
    },
  };

  submitBtn.disabled = true;
  try {
    const result = await saveReport(report);
    const saved = result.signal || report;

    // Deep-link the success button to the new pin on the dashboard map.
    const { lat, lng } = saved.metadata || {};
    if (lat != null && lng != null) {
      document.getElementById("viewOnDashboard").href =
        `dashboard.html?focus=${lat},${lng}`;
    }
    document.getElementById("successNote").textContent =
      result.storage === "local"
        ? "The server was unreachable, so this report is saved in your browser only for now."
        : "Saved to CivicPulse — other residents can now see and verify it.";

    document.getElementById("reportForm").hidden = true;
    document.getElementById("reportSuccess").hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err) {
    showError(err.message || "Could not submit report. Please try again.");
  } finally {
    submitBtn.disabled = false;
  }
});

document.getElementById("reportAnother").addEventListener("click", () => {
  window.location.reload();
});
