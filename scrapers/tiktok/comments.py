import json
import time
import urllib.parse
from dataclasses import asdict, dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.tiktok.config import TikTokScrapeConfig
from scrapers.tiktok.driver import create_tiktok_driver
from scrapers.tiktok.ui import dismiss_overlays, find_comment_container, open_comments_panel

TIKTOK_SEARCH_URL = "https://www.tiktok.com/search/video"
COMMENT_SCROLL_PAUSE_SEC = 1.5


@dataclass
class TikTokComment:
    author: str
    text: str
    video_url: str
    search_query: str
    scraped_at: float


def _build_search_url(query: str) -> str:
    encoded = urllib.parse.quote(query)
    return f"{TIKTOK_SEARCH_URL}?q={encoded}"


def _collect_video_links(driver, limit: int) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()

    for anchor in driver.find_elements(By.CSS_SELECTOR, "a[href*='/video/']"):
        href = anchor.get_attribute("href")
        if not href or href in seen:
            continue
        seen.add(href)
        links.append(href)
        if len(links) >= limit:
            break

    return links


def _scroll_comments(driver, max_comments: int) -> None:
    last_count = 0
    stagnant_rounds = 0
    comment_container = find_comment_container(driver)
    comment_selector = (
        "div[data-e2e='comment-level-1'], "
        "div[class*='CommentItem'], "
        "span[data-e2e='comment-level-1']"
    )

    while stagnant_rounds < 3:
        comments = driver.find_elements(By.CSS_SELECTOR, comment_selector)
        if len(comments) >= max_comments:
            break
        if len(comments) == last_count:
            stagnant_rounds += 1
        else:
            stagnant_rounds = 0
            last_count = len(comments)

        if comment_container:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight",
                comment_container,
            )
        else:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(COMMENT_SCROLL_PAUSE_SEC)


def _comment_author(node) -> str:
    author_selectors = (
        "a[data-e2e='comment-username']",
        "a[href*='/@']",
        "span[class*='UserName']",
        "p[data-e2e='comment-username']",
    )
    for selector in author_selectors:
        try:
            author = node.find_element(By.CSS_SELECTOR, selector).text.strip()
            if author:
                return author
        except Exception:
            continue
    return "unknown"


def _parse_comments(driver, video_url: str, search_query: str, limit: int) -> list[TikTokComment]:
    scraped_at = time.time()
    comments: list[TikTokComment] = []
    seen_text: set[str] = set()

    for node in driver.find_elements(
        By.CSS_SELECTOR,
        "div[data-e2e='comment-level-1'], div[class*='CommentItem']",
    ):
        try:
            author = _comment_author(node)
            text = node.find_element(
                By.CSS_SELECTOR,
                "span[data-e2e='comment-level-1'], p[class*='CommentText']",
            ).text.strip()
        except Exception:
            continue

        if not text or text in seen_text:
            continue
        seen_text.add(text)

        comments.append(
            TikTokComment(
                author=author,
                text=text,
                video_url=video_url,
                search_query=search_query,
                scraped_at=scraped_at,
            )
        )
        if len(comments) >= limit:
            return comments

    for span in driver.find_elements(By.CSS_SELECTOR, "span[data-e2e='comment-level-1']"):
        text = span.text.strip()
        if not text or text in seen_text:
            continue
        seen_text.add(text)

        author = "unknown"
        try:
            parent = span.find_element(
                By.XPATH,
                "./ancestor::div[contains(@class, 'Comment') or @data-e2e][1]",
            )
            author = _comment_author(parent)
        except Exception:
            pass

        comments.append(
            TikTokComment(
                author=author,
                text=text,
                video_url=video_url,
                search_query=search_query,
                scraped_at=scraped_at,
            )
        )
        if len(comments) >= limit:
            break

    return comments


def _load_video_comments(
    driver,
    video_url: str,
    *,
    search_query: str,
    max_comments: int,
    reload_on_retry: bool = True,
) -> list[TikTokComment]:
    """Open the comments panel and parse comments, with retries if blocked by overlays."""

    def attempt(label: str) -> list[TikTokComment]:
        print(f"  {label}")
        dismiss_overlays(driver)
        opened = open_comments_panel(driver)
        if not opened:
            print("  warning: could not open comments panel")
        time.sleep(1.5)
        _scroll_comments(driver, max_comments)
        comments = _parse_comments(
            driver,
            video_url=video_url,
            search_query=search_query,
            limit=max_comments,
        )
        print(f"  found {len(comments)} comments")
        return comments

    comments = attempt("loading comments")
    if comments:
        return comments

    print("  retry: dismissing overlays and reopening comments panel")
    time.sleep(2)
    dismiss_overlays(driver)
    open_comments_panel(driver)
    time.sleep(2)
    _scroll_comments(driver, max_comments)
    comments = _parse_comments(
        driver,
        video_url=video_url,
        search_query=search_query,
        limit=max_comments,
    )
    if comments:
        print(f"  retry succeeded with {len(comments)} comments")
        return comments

    if reload_on_retry:
        print("  retry: reloading video page")
        driver.get(video_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(4)
        comments = attempt("loading comments after reload")
        if comments:
            return comments

    return []


def scrape_comments_from_video(
    video_url: str,
    *,
    max_comments: int = 25,
    headless: bool = False,
) -> list[TikTokComment]:
    """
    Scrape comments from a single TikTok video URL.

    Useful for testing the comment parser without search/login.
    TikTok may still gate comments behind a login wall — if that happens,
    the browser will stay open long enough to inspect, and you'll get 0 comments.
    """
    driver = create_tiktok_driver(headless=headless)
    try:
        print(f"Opening {video_url}")
        comments = _scrape_video_with_driver(
            driver,
            video_url,
            search_query="direct_video",
            max_comments=max_comments,
        )
        print(f"Found {len(comments)} comments")
        if not comments:
            print(
                "No comments found. A TikTok overlay may still be blocking the page, "
                "or the comment selectors need updating."
            )
            # Keep the window open briefly so you can see what TikTok showed.
            time.sleep(8)
        return comments
    finally:
        driver.quit()


def _scrape_video_with_driver(
    driver,
    video_url: str,
    *,
    search_query: str,
    max_comments: int,
) -> list[TikTokComment]:
    driver.get(video_url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(2)
    return _load_video_comments(
        driver,
        video_url,
        search_query=search_query,
        max_comments=max_comments,
    )


def scrape_comments_for_area(config: TikTokScrapeConfig) -> list[TikTokComment]:
    """
    Search TikTok for civic-issue videos in a geographic area and scrape comments.

    TikTok's DOM changes frequently; selectors here are a starting point and will
    likely need tuning as we iterate on this branch.
    """
    driver = create_tiktok_driver(headless=config.headless)
    all_comments: list[TikTokComment] = []

    try:
        for query in config.search_queries():
            driver.get(_build_search_url(query))
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/video/']"))
            )
            time.sleep(2)

            for video_url in _collect_video_links(driver, config.max_videos_per_query):
                all_comments.extend(
                    _scrape_video_with_driver(
                        driver,
                        video_url,
                        search_query=query,
                        max_comments=config.max_comments_per_video,
                    )
                )
    finally:
        driver.quit()

    return all_comments


def _write_comments_json(comments: list[TikTokComment], output_path: str) -> int:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([asdict(c) for c in comments], f, indent=2)
    return len(comments)


def scrape_comments_to_json(config: TikTokScrapeConfig, output_path: str) -> int:
    return _write_comments_json(scrape_comments_for_area(config), output_path)


def scrape_video_to_json(
    video_url: str,
    output_path: str,
    *,
    max_comments: int = 25,
    headless: bool = False,
) -> int:
    comments = scrape_comments_from_video(
        video_url,
        max_comments=max_comments,
        headless=headless,
    )
    return _write_comments_json(comments, output_path)
