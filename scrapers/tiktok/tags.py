import json
import re
import time
from dataclasses import asdict, dataclass, field
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.tiktok.comments import TikTokComment, _load_video_comments
from scrapers.tiktok.driver import close_tiktok_driver, create_tiktok_driver
from scrapers.tiktok.ui import dismiss_overlays

FEED_SCROLL_PAUSE_SEC = 1.5


@dataclass
class TikTokVideo:
    url: str
    tag: str
    tag_url: str
    author: str = ""
    caption: str = ""
    like_count: str = ""
    comment_count: str = ""
    share_count: str = ""
    comments: list[TikTokComment] = field(default_factory=list)
    scraped_at: float = 0.0


@dataclass
class TikTokTagResult:
    tag: str
    tag_url: str
    videos: list[TikTokVideo] = field(default_factory=list)
    scraped_at: float = 0.0


def _tag_name_from_url(tag_url: str) -> str:
    path = urlparse(tag_url).path.strip("/")
    if path.startswith("tag/"):
        return path.split("/", 1)[1]
    return path.rsplit("/", 1)[-1]


def _normalize_video_url(url: str) -> str:
    return url.split("?", 1)[0]


def _author_from_video_url(video_url: str) -> str:
    match = re.search(r"tiktok\.com/@([^/]+)/video/", video_url)
    return match.group(1) if match else ""


def _first_text(driver, selectors: tuple[str, ...]) -> str:
    for selector in selectors:
        try:
            text = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
            if text:
                return text
        except Exception:
            continue
    return ""


def _collect_video_links(driver, limit: int) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()

    for anchor in driver.find_elements(By.CSS_SELECTOR, "a[href*='/video/']"):
        href = anchor.get_attribute("href")
        if not href:
            continue
        href = _normalize_video_url(href)
        if href in seen:
            continue
        seen.add(href)
        links.append(href)
        if len(links) >= limit:
            break

    return links


def _scroll_tag_feed(driver, target_video_count: int) -> None:
    last_count = 0
    stagnant_rounds = 0

    while stagnant_rounds < 4:
        current_count = len(_collect_video_links(driver, target_video_count * 3))
        if current_count >= target_video_count:
            break
        if current_count == last_count:
            stagnant_rounds += 1
        else:
            stagnant_rounds = 0
            last_count = current_count

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(FEED_SCROLL_PAUSE_SEC)


def _parse_video_page(
    driver,
    video_url: str,
    *,
    tag: str,
    tag_url: str,
    max_comments: int,
) -> TikTokVideo:
    scraped_at = time.time()
    author = _first_text(
        driver,
        (
            "h2[data-e2e='browse-username']",
            "a[data-e2e='browse-username']",
            "span[data-e2e='browse-username']",
        ),
    ) or _author_from_video_url(video_url)
    caption = _first_text(
        driver,
        (
            "div[data-e2e='browse-video-desc']",
            "div[data-e2e='video-desc']",
            "h1[data-e2e='browse-video-desc']",
        ),
    )
    like_count = _first_text(driver, ("strong[data-e2e='like-count']",))
    comment_count = _first_text(driver, ("strong[data-e2e='comment-count']",))
    share_count = _first_text(driver, ("strong[data-e2e='share-count']",))

    comments = _load_video_comments(
        driver,
        video_url,
        search_query=f"tag:{tag}",
        max_comments=max_comments,
    )

    return TikTokVideo(
        url=video_url,
        tag=tag,
        tag_url=tag_url,
        author=author,
        caption=caption,
        like_count=like_count,
        comment_count=comment_count,
        share_count=share_count,
        comments=comments,
        scraped_at=scraped_at,
    )


def scrape_tag(
    tag_url: str,
    *,
    max_videos: int = 5,
    max_comments_per_video: int = 25,
    headless: bool = False,
) -> TikTokTagResult:
    tag = _tag_name_from_url(tag_url)
    driver = create_tiktok_driver(headless=headless)
    videos: list[TikTokVideo] = []

    try:
        print(f"Opening tag page: {tag_url}")
        driver.get(tag_url)
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        dismiss_overlays(driver)

        _scroll_tag_feed(driver, max_videos)
        video_urls = _collect_video_links(driver, max_videos)

        # TikTok intermittently serves a "Something went wrong" shell with no
        # feed; a reload usually recovers it.
        for attempt in range(2):
            if video_urls:
                break
            print(f"No videos rendered for #{tag}, refreshing (attempt {attempt + 1}/2)")
            driver.refresh()
            time.sleep(5)
            dismiss_overlays(driver)
            _scroll_tag_feed(driver, max_videos)
            video_urls = _collect_video_links(driver, max_videos)

        print(f"Found {len(video_urls)} videos for #{tag}")

        for index, video_url in enumerate(video_urls, start=1):
            print(f"  [{index}/{len(video_urls)}] {video_url}")
            driver.get(video_url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            dismiss_overlays(driver)

            video = _parse_video_page(
                driver,
                video_url,
                tag=tag,
                tag_url=tag_url,
                max_comments=max_comments_per_video,
            )
            print(f"    author={video.author or 'unknown'} comments={len(video.comments)}")
            videos.append(video)
    finally:
        close_tiktok_driver(driver)

    return TikTokTagResult(
        tag=tag,
        tag_url=tag_url,
        videos=videos,
        scraped_at=time.time(),
    )


def scrape_tags(
    tag_urls: list[str],
    *,
    max_videos: int = 5,
    max_comments_per_video: int = 25,
    headless: bool = False,
) -> list[TikTokTagResult]:
    results: list[TikTokTagResult] = []
    for tag_url in tag_urls:
        results.append(
            scrape_tag(
                tag_url,
                max_videos=max_videos,
                max_comments_per_video=max_comments_per_video,
                headless=headless,
            )
        )
    return results


def _video_to_dict(video: TikTokVideo) -> dict:
    payload = asdict(video)
    payload["comments"] = [asdict(comment) for comment in video.comments]
    return payload


def _tag_result_to_dict(result: TikTokTagResult) -> dict:
    return {
        "tag": result.tag,
        "tag_url": result.tag_url,
        "scraped_at": result.scraped_at,
        "video_count": len(result.videos),
        "videos": [_video_to_dict(video) for video in result.videos],
    }


def scrape_tags_to_json(
    tag_urls: list[str],
    output_path: str,
    *,
    max_videos: int = 5,
    max_comments_per_video: int = 25,
    headless: bool = False,
) -> tuple[dict[str, int], list[TikTokTagResult]]:
    results = scrape_tags(
        tag_urls,
        max_videos=max_videos,
        max_comments_per_video=max_comments_per_video,
        headless=headless,
    )

    payload = {
        "tag_count": len(results),
        "tags": [_tag_result_to_dict(result) for result in results],
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    counts = {
        "tags": len(results),
        "videos": sum(len(result.videos) for result in results),
        "comments": sum(
            len(video.comments) for result in results for video in result.videos
        ),
    }
    return counts, results
