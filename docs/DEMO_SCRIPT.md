# CivicPulse — 10-minute mayor demo script

**Audience:** Mayor's office staff, first time seeing CivicPulse.
**Setup:** Server running (`py run.py`), signals imported, demo researches seeded (`py scripts/seed_demo.py`).

---

## 1. Dashboard overview (2 min)

Open **dashboard.html**.

> "This is the CivicPulse command center. Every card is a signal — a news article, social media post, or community report that mentions a civic issue in Irvine."

Point out:
- **Category tags** on each card (housing, potholes, public safety, etc.)
- **Method chip** (keywords, model, keywords + model) — "This shows how the system classified each signal. Some are caught by keywords, some by the model, some by both."
- **Match strength** (Strong / Moderate / Weak) — "This is how confident the system is. We show a qualitative band, not a fake percentage, because the model is still learning."
- **Source mix** — news articles alongside TikTok comments and Reddit posts.

## 2. Source analytics (1 min)

Click into **source.html** (or click a source label on a card).

> "You can drill into any source — see how many signals it contributes, filter by match strength, and spot patterns by outlet or category."

Point out the **match strength** stat (now "Strong" / "Moderate" / "Weak", not a misleading percentage).

## 3. Create a new research (3 min)

Navigate to **research.html** (New Research).

> "This is where staff creates a research topic. Let's say the mayor wants to understand what people are saying about housing."

1. **Type a topic:** "Affordable housing in Irvine neighborhoods"
   - Watch the expansion pills appear after the title settles (topic keywords auto-suggested)
2. **Select a few keyword chips** — "rent", "housing prices", "lease"
3. **Point out the category picker** — housing auto-inferred from expansions
4. **Scroll to listen sources** — "We can listen to news, TikTok, Reddit. Twitter and YouTube are armed but not yet live — they show 'Archive only'."
5. **Extract checkboxes** — "We can ask for sentiment analysis, narrative clustering, policy asks. Misinfo and bot detection are optional."
6. **Right rail** — "This shows an estimate from our archive: how many signals we already have for these sources."
7. **Click "Launch scrape"** — creates the research, sets status to gathering, queues jobs.

> "The system now searches our archive and, for sources with live scrapers, kicks off new data collection."

## 4. Research workspace (3 min)

The page redirects to **research-detail.html**.

> "This is the workspace. Everything about this research lives here."

Walk through tabs:
- **Archive tab** — "These are signals matched from our existing database. Each one shows the title, body snippet, category, source, and a relevance score."
  - Click "Run Archive" if needed to refresh
- **Map tab** — "When signals have location data, they appear on this map of Irvine. Right now most signals don't have coordinates — that's a future enrichment."
- **Jobs tab** — "This shows scrape jobs linked to this research. You can start a new one for irvine-news or tiktok."
- **Summary tab** — "This is a quick briefing view. Click 'Print Summary' for a one-page PDF."

## 5. Print summary (1 min)

Click **Print Summary** to open the summary page.

> "This is the printable research briefing. It shows the overview stats, top signals, and — based on which extract options were checked — sections for sentiment, clustering, policy asks."

Point out:
- Stats grid with signal counts by category
- Top signals with source attribution
- Extract sections (currently showing "Analysis pending" placeholders — these will be populated as the analysis pipeline matures)
- Footer with generation date

> "Staff can print this or save as PDF for the mayor's briefing."

---

## Talking points for Q&A

**"How accurate is the classification?"**
> We show match strength as Strong / Moderate / Weak — not a fake percentage. The system uses keyword matching and a lightweight model. We're continuously improving by adding training examples from real signals.

**"Where does the data come from?"**
> Local news outlets (Irvine Weekly, Voice of OC, etc.), TikTok comments on Irvine-tagged videos, and Reddit posts from local subreddits. Twitter, YouTube, and Facebook are structured but not yet live.

**"Can anyone run a scrape?"**
> No. Scraping requires a dev account on a local machine. The hosted site (Render) only shows the dashboard and research tools — it never starts scrape jobs.

**"What about privacy?"**
> We only collect publicly available posts. No DMs, no private groups, no personally identifiable information beyond what's already public. The ethics gate on the compose page is a static checklist reminding staff to review before launching.

---

## Pre-demo checklist

- [ ] Server running: `py run.py`
- [ ] Signals imported (950+ in DB): `py scripts/seed_demo.py --check`
- [ ] Demo researches seeded: `py scripts/seed_demo.py`
- [ ] Browser window sized for presentation (1280+ wide)
- [ ] No `.env` or credentials visible in any terminal
