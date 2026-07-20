# TikTok scrape (desktop Chrome)

TikTok scraping uses **Selenium + undetected-chromedriver** on a **local desktop** with Google Chrome. **Anonymous (no-login) browsing is the default** — the same way you’d open a tag/video and comments in a normal Chrome window without signing in.

A dedicated TikTok account is **optional**. Only log in if comments stay blocked after overlays are dismissed.

## Default: no login

```bash
python scripts/scrape_tiktok.py --tag-url "https://www.tiktok.com/tag/irvine" --max-videos 3 --max-comments 10
```

Do **not** pass `--headless` for reliable results. The scraper:

1. Opens Chrome with a persistent profile under `data/chrome/tiktok_profile/` (cookies / dismissed popups stick; login not required)
2. Dismisses overlays carefully (cookies, “got it”, **Not now** on login popups — avoids generic Close/Esc that can strand you on a login page)
3. Opens the comments panel and scrapes

Guest pages always show **Log in / Sign up** in the header — that alone is normal.

If a **“you need to log in”** interstitial appears after the comment click: the scraper tries **Not now** / modal X / one Esc, then continues or skips that video. Leave the Chrome window open while it runs — closing it mid-job will stop the scrape.

Override the profile directory with `CIVICPULSE_CHROME_PROFILE` if needed.

## Optional login (only if needed)

If a real login modal keeps blocking comments:

1. Run a small headed scrape
2. In the Chrome window, dismiss the popup or log in once
3. Retry — the session stays in `data/chrome/tiktok_profile/`

## Comment panel

Overlays are dismissed, then the comments panel is opened with retries. Per-video comment failures print a warning and continue the job (they do not abort the whole scrape).

## Jobs API

Dashboard `/api/jobs` for `source: "tiktok"` runs the same CLI. Chrome start failures still surface clearly in `error` / `log`. Soft login hints may appear in the log without failing the job.

## Not supported

- Headless TikTok on a remote server
- Sharing one Chrome profile across concurrent scrapes (run one TikTok job at a time)
- Opening the CivicPulse Chrome profile while another Chrome window already has that same `user-data-dir` locked — close other sessions using `data/chrome/tiktok_profile` first
