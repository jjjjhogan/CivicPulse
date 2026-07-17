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
    categories: ["traffic_safety"],
    published_utc: "2026-07-02",
    metadata: {
      lat: 33.6695,
      lng: -117.8231,
      classification: {
        scores: { traffic_safety: 0.82 },
        confidence: 0.82,
        method: "model",
        model_version: "nb-v1",
        rescued: true,
      },
    },
  },
  {
    source: "tiktok",
    outlet: "@irvinemoms",
    title: "POV: the pothole on Culver ate my coffee again #irvine #potholes",
    url: "https://www.tiktok.com/tag/irvine",
    categories: ["potholes"],
    published_utc: "2026-07-01",
    metadata: {
      lat: 33.6846,
      lng: -117.7998,
      classification: {
        scores: { potholes: 0.87 },
        confidence: 0.87,
        method: "keywords+model",
        model_version: "nb-v1",
      },
    },
  },
  {
    source: "news",
    outlet: "Irvine Standard",
    title: "No. 3 city in America to raise a family",
    url: "https://www.irvinestandard.com/",
    categories: ["public_safety"],
    published_utc: "2026-07-01",
    metadata: {
      classification: {
        scores: { public_safety: 0.3 },
        confidence: 0.3,
        method: "outlet_default",
        model_version: "nb-v1",
      },
    },
  },
  {
    source: "reddit",
    outlet: "r/irvine",
    title: "Pothole on Culver and Alton has been there for a month now",
    url: "https://www.reddit.com/r/irvine/",
    categories: ["potholes"],
    published_utc: "2026-06-30",
    metadata: {
      lat: 33.6603,
      lng: -117.8005,
      classification: {
        scores: { potholes: 0.7 },
        confidence: 0.7,
        method: "keywords",
        model_version: "nb-v1",
      },
    },
  },
  {
    source: "tiktok",
    outlet: "@ocpulsecheck",
    title: "Rent in Irvine just went up AGAIN — here's what residents told me",
    url: "https://www.tiktok.com/tag/irvinehousing",
    categories: ["housing"],
    published_utc: "2026-06-29",
    metadata: {
      lat: 33.6926,
      lng: -117.8352,
      classification: {
        scores: { housing: 0.8 },
        confidence: 0.8,
        method: "keywords",
        model_version: "nb-v1",
      },
    },
  },
  {
    source: "news",
    outlet: "Voice of OC",
    title: "37 People Died 'Without Fixed Abode' in OC in May, the Highest Monthly Total in a Year",
    url: "https://voiceofoc.org/",
    categories: ["housing"],
    published_utc: "2026-06-28",
    metadata: {
      classification: {
        scores: { housing: 0.88 },
        confidence: 0.88,
        method: "model",
        model_version: "nb-v1",
        rescued: true,
      },
    },
  },
  {
    source: "reddit",
    outlet: "r/irvine",
    title: "Construction noise starting before 7am near Woodbury — anyone else?",
    url: "https://www.reddit.com/r/irvine/",
    categories: ["noise"],
    published_utc: "2026-06-27",
    metadata: {
      lat: 33.7093,
      lng: -117.7411,
      classification: {
        scores: { noise: 0.77 },
        confidence: 0.77,
        method: "keywords+model",
        model_version: "nb-v1",
      },
    },
  },
  {
    source: "tiktok",
    outlet: "@uciweekly",
    title: "Streetlights out near campus for 2 weeks — students walking home in the dark",
    url: "https://www.tiktok.com/tag/uci",
    categories: ["public_safety"],
    published_utc: "2026-06-26",
    metadata: {
      lat: 33.6405,
      lng: -117.8443,
      classification: {
        scores: { public_safety: 0.7 },
        confidence: 0.7,
        method: "keywords",
        model_version: "nb-v1",
      },
    },
  },
  {
    source: "news",
    outlet: "Irvine Weekly",
    title: "City council weighs new recycling and trash pickup schedule",
    url: "https://irvineweekly.com/",
    categories: ["sanitation"],
    published_utc: "2026-06-25",
    metadata: {
      lat: 33.6784,
      lng: -117.7713,
      classification: {
        scores: { sanitation: 0.9 },
        confidence: 0.9,
        method: "keywords",
        model_version: "nb-v1",
      },
    },
  },
  {
    source: "reddit",
    outlet: "r/irvine",
    title: "Illegal dumping behind the Northwood shopping plaza is getting worse",
    url: "https://www.reddit.com/r/irvine/",
    categories: ["sanitation"],
    published_utc: "2026-06-24",
    metadata: {
      lat: 33.7152,
      lng: -117.7846,
      classification: {
        scores: { sanitation: 0.8 },
        confidence: 0.8,
        method: "keywords",
        model_version: "nb-v1",
      },
    },
  },
];

// Mirrors CATEGORY_KEYWORDS in scrapers/categories.py — used so the keyword
// search also matches category keywords, not just words in the title.
const CATEGORY_KEYWORDS = {
  potholes: ["pothole", "road damage", "pavement crack", "street repair", "road repair"],
  noise: ["noise complaint", "loud music", "construction noise", "loud neighbors", "fireworks"],
  sanitation: ["trash pickup", "garbage", "illegal dumping", "sanitation", "recycling"],
  violent_crime: ["shooting", "assault", "robbery", "stabbing", "murder", "homicide"],
  property_crime: ["theft", "stolen", "break-in", "burglary", "vandalism", "shoplifting"],
  traffic_safety: ["crash", "hit and run", "speeding", "crosswalk", "reckless driving", "pursuit"],
  emergencies: ["flood", "flooding", "wildfire", "evacuation", "hazmat", "emergency"],
  public_safety: ["crime", "police", "arrest", "protest", "streetlight out", "missing person"],
  housing: ["eviction", "rent increase", "affordable housing", "homeless", "housing crisis", "rent"],
  immigration: ["immigration", "immigrant", "deportation", "ice raid", "ice protest", "migrant"],
};

const CATEGORY_COLORS = {
  potholes: "#b07a1e",
  noise: "#8a5fc9",
  sanitation: "#4c7a34",
  violent_crime: "#8f2b2b",
  property_crime: "#b3486e",
  traffic_safety: "#546e7a",
  emergencies: "#d1571c",
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

// Classification metadata written by scrapers/classifier.py — scores,
// confidence, method — lives in metadata.classification. Resident reports
// and pre-classifier scrapes don't have it ("unscored").
function signalClassification(signal) {
  return signal.metadata?.classification || null;
}

function signalConfidence(signal) {
  const confidence = signalClassification(signal)?.confidence;
  return typeof confidence === "number" ? confidence : null;
}

// Rescued signals are "missed stories": the keyword pass found nothing and
// the model pass caught them anyway.
function isRescuedSignal(signal) {
  return Boolean(signalClassification(signal)?.rescued);
}

const CONFIDENCE_BANDS = {
  high: { label: "High", min: 0.75, color: "#4c7a34" },
  medium: { label: "Medium", min: 0.5, color: "#b07a1e" },
  low: { label: "Low", min: 0, color: "#c44f3f" },
  unscored: { label: "Unscored", color: "#8a8f98" },
};

function confidenceBand(signal) {
  const confidence = signalConfidence(signal);
  if (confidence == null) return "unscored";
  if (confidence >= CONFIDENCE_BANDS.high.min) return "high";
  if (confidence >= CONFIDENCE_BANDS.medium.min) return "medium";
  return "low";
}

// How a signal got its categories, in words a resident would use.
const CLASSIFICATION_METHODS = {
  keywords: "Matched issue keywords",
  "keywords+model": "Matched issue keywords, confirmed by the model",
  model: "Caught by the model — no keyword matched",
  inherited: "Inherited from the video it comments on",
  outlet_default: "Assumed from a trusted news outlet",
  legacy: "Classified by an earlier pipeline",
  none: "No civic issue detected",
};

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
