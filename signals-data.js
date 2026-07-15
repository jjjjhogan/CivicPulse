// Shared signal data and helpers used by dashboard.js and source.js.
//
// Sample records follow the CivicSignal schema (scrapers/schema.py):
// { source, outlet, title, body, url, categories, published_utc, metadata }
// with optional metadata.lat / metadata.lng for map placement.
// When scripts/dashboard_server.py is running, live signals load from
// GET /api/signals and replace the sample social records below.

const SAMPLE_SIGNALS = [
  {
    source: "news",
    outlet: "Voice of OC",
    title: "Orange County's Growing E-bike Crackdown Continues Targeting Parents",
    url: "https://voiceofoc.org/",
    categories: ["public_safety"],
    published_utc: "2026-07-02",
    metadata: { lat: 33.6695, lng: -117.8231 },
  },
  {
    source: "tiktok",
    outlet: "@irvinemoms",
    title: "POV: the pothole on Culver ate my coffee again #irvine #potholes",
    url: "https://www.tiktok.com/tag/irvine",
    categories: ["potholes"],
    published_utc: "2026-07-01",
    metadata: { lat: 33.6846, lng: -117.7998 },
  },
  {
    source: "news",
    outlet: "Irvine Standard",
    title: "No. 3 city in America to raise a family",
    url: "https://www.irvinestandard.com/",
    categories: ["public_safety"],
    published_utc: "2026-07-01",
    metadata: {},
  },
  {
    source: "reddit",
    outlet: "r/irvine",
    title: "Pothole on Culver and Alton has been there for a month now",
    url: "https://www.reddit.com/r/irvine/",
    categories: ["potholes"],
    published_utc: "2026-06-30",
    metadata: { lat: 33.6603, lng: -117.8005 },
  },
  {
    source: "tiktok",
    outlet: "@ocpulsecheck",
    title: "Rent in Irvine just went up AGAIN — here's what residents told me",
    url: "https://www.tiktok.com/tag/irvinehousing",
    categories: ["housing"],
    published_utc: "2026-06-29",
    metadata: { lat: 33.6926, lng: -117.8352 },
  },
  {
    source: "news",
    outlet: "Voice of OC",
    title: "37 People Died 'Without Fixed Abode' in OC in May, the Highest Monthly Total in a Year",
    url: "https://voiceofoc.org/",
    categories: ["housing"],
    published_utc: "2026-06-28",
    metadata: {},
  },
  {
    source: "reddit",
    outlet: "r/irvine",
    title: "Construction noise starting before 7am near Woodbury — anyone else?",
    url: "https://www.reddit.com/r/irvine/",
    categories: ["noise"],
    published_utc: "2026-06-27",
    metadata: { lat: 33.7093, lng: -117.7411 },
  },
  {
    source: "tiktok",
    outlet: "@uciweekly",
    title: "Streetlights out near campus for 2 weeks — students walking home in the dark",
    url: "https://www.tiktok.com/tag/uci",
    categories: ["public_safety"],
    published_utc: "2026-06-26",
    metadata: { lat: 33.6405, lng: -117.8443 },
  },
  {
    source: "news",
    outlet: "Irvine Weekly",
    title: "City council weighs new recycling and trash pickup schedule",
    url: "https://irvineweekly.com/",
    categories: ["sanitation"],
    published_utc: "2026-06-25",
    metadata: { lat: 33.6784, lng: -117.7713 },
  },
  {
    source: "reddit",
    outlet: "r/irvine",
    title: "Illegal dumping behind the Northwood shopping plaza is getting worse",
    url: "https://www.reddit.com/r/irvine/",
    categories: ["sanitation"],
    published_utc: "2026-06-24",
    metadata: { lat: 33.7152, lng: -117.7846 },
  },
];

// Mirrors CATEGORY_KEYWORDS in scrapers/categories.py — used so the keyword
// search also matches category keywords, not just words in the title.
const CATEGORY_KEYWORDS = {
  potholes: ["pothole", "road damage", "pavement crack", "street repair", "road repair"],
  noise: ["noise complaint", "loud music", "construction noise", "loud neighbors", "fireworks"],
  sanitation: ["trash pickup", "garbage", "illegal dumping", "sanitation", "recycling"],
  public_safety: [
    "break-in", "shooting", "assault", "streetlight out", "crime", "police",
    "flood", "flooding", "protest", "crash", "emergency", "pursuit",
  ],
  housing: ["eviction", "rent increase", "affordable housing", "homeless", "housing crisis", "rent"],
  immigration: ["immigration", "immigrant", "deportation", "ice raid", "ice protest", "migrant"],
};

const CATEGORY_COLORS = {
  potholes: "#b07a1e",
  noise: "#8a5fc9",
  sanitation: "#4c7a34",
  public_safety: "#c44f3f",
  housing: "#3a63c4",
  immigration: "#2f6f6a",
};

const SOURCE_LABELS = {
  tiktok: "TikTok",
  news: "News",
  reddit: "Reddit",
  twitter: "Twitter",
  resident: "Resident",
};

// Sources always shown in source pickers, even with zero signals.
const MAIN_SOURCES = ["tiktok", "reddit", "twitter", "news", "resident"];

// Sources whose sample records are replaced by live scraper data.
const LIVE_SOURCES = ["tiktok", "reddit", "twitter", "news"];

// Resident reports submitted through report.html (stored locally until a
// backend /api/reports endpoint exists).
const REPORTS_STORAGE_KEY = "civicpulse_resident_reports";

function loadResidentReports() {
  try {
    return JSON.parse(localStorage.getItem(REPORTS_STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

// Combine resident reports, sample records, and live scraper signals into
// one signal list. With no live data the samples stand in for everything.
function buildSignals(liveSignals) {
  const reports = loadResidentReports();
  if (!liveSignals || !liveSignals.length) {
    return [...reports, ...SAMPLE_SIGNALS];
  }
  const other = SAMPLE_SIGNALS.filter((s) => !LIVE_SOURCES.includes(s.source));
  return [...reports, ...other, ...liveSignals];
}

// Signals have no id, so key detail pages on fields that identify one.
function signalKey(signal) {
  return [signal.source, signal.published_utc, signal.title].join("|");
}

function signalUrl(signal) {
  return `signal.html?id=${encodeURIComponent(signalKey(signal))}`;
}

// Fetch live signals from the Flask backend; empty when it isn't running.
async function fetchLiveSignals() {
  try {
    const res = await fetch("/api/signals");
    if (!res.ok) return [];
    const data = await res.json();
    return data.signals || [];
  } catch {
    return [];
  }
}
