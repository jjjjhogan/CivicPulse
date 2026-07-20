// Sample records in the shape produced by the ingestion scrapers
// (reddit_scraper.py / irvine_news_scraper.py). Prefer GET /api/signals/feed
// when dashboard_server.py is running (SQLite after import).
// Named LANDING_* because signals-data.js (loaded first) already defines
// its own SAMPLE_SIGNALS.
const LANDING_SAMPLE_SIGNALS = [
  {
    outlet: "Voice of OC",
    title: "Orange County's Growing E-bike Crackdown Continues Targeting Parents",
    categories: ["traffic_safety"],
    published_utc: "2026-07-02",
  },
  {
    outlet: "Irvine Standard",
    title: "No. 3 city in America to raise a family",
    categories: ["public_safety"],
    published_utc: "2026-07-01",
  },
  {
    outlet: "r/irvine",
    title: "Pothole on Culver and Alton has been there for a month now",
    categories: ["potholes"],
    published_utc: "2026-06-30",
  },
  {
    outlet: "Voice of OC",
    title: "37 People Died 'Without Fixed Abode' in OC in May, the Highest Monthly Total in a Year",
    categories: ["housing"],
    published_utc: "2026-06-28",
  },
  {
    outlet: "r/irvine",
    title: "Construction noise starting before 7am near Woodbury — anyone else?",
    categories: ["noise"],
    published_utc: "2026-06-27",
  },
  {
    outlet: "Irvine Weekly",
    title: "City council weighs new recycling and trash pickup schedule",
    categories: ["sanitation"],
    published_utc: "2026-06-25",
  },
];

function renderSignals(records) {
  const container = document.getElementById("signalCards");
  container.innerHTML = "";

  for (const record of records) {
    const card = document.createElement("article");
    card.className = "card";

    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = record.categories.join(", ").replaceAll("_", " ");

    const title = document.createElement("h3");
    title.textContent = record.title;

    const meta = document.createElement("p");
    meta.className = "meta";
    meta.textContent = `${record.outlet} · ${publishedAgo(record.published_utc)}`;
    meta.title = record.published_utc || "";

    card.append(tag, title, meta);
    container.appendChild(card);
  }
}

async function loadLandingSignals() {
  try {
    const res = await fetch("/api/signals/feed");
    if (res.ok) {
      const data = await res.json();
      const signals = data.signals || [];
      if (signals.length) {
        renderSignals(signals);
        return;
      }
    }
  } catch {
    // Server not running — fall through to samples.
  }
  renderSignals(LANDING_SAMPLE_SIGNALS);
}

loadLandingSignals();
