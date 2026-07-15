import json
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.tiktok.caption import extract_caption
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
    hashtags: list[str] = field(default_factory=list)
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
    return url.split("?", 1)[0].rstrip("/")


def _author_from_video_url(video_url: str) -> str:
    match = re.search(r"tiktok\.com/@([^/]+)/video/", video_url)
    return match.group(1) if match else ""


def load_existing_video_urls(path: str | Path) -> set[str]:
    """Return normalized video URLs already present in a raw scrape JSON file."""
    file_path = Path(path)
    if not file_path.is_file():
        return set()
    try:
        with open(file_path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return set()

    urls: set[str] = set()
    for tag in payload.get("tags") or []:
        for video in tag.get("videos") or []:
            url = video.get("url") or ""
            if url:
                urls.add(_normalize_video_url(url))
    return urls


def load_raw_payload(path: str | Path) -> dict:
    file_path = Path(path)
    if not file_path.is_file():
        return {"tag_count": 0, "tags": []}
    try:
        with open(file_path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {"tag_count": 0, "tags": []}
    if not isinstance(payload, dict):
        return {"tag_count": 0, "tags": []}
    payload.setdefault("tags", [])
    return payload


def dedupe_raw_payload(payload: dict) -> tuple[dict, int]:
    """Keep one copy of each video URL (first wins). Returns (payload, removed)."""
    seen: set[str] = set()
    removed = 0
    tags_out: list[dict] = []

    for tag in payload.get("tags") or []:
        videos_out: list[dict] = []
        for video in tag.get("videos") or []:
            url = _normalize_video_url(video.get("url") or "")
            if not url or url in seen:
                removed += 1
                continue
            seen.add(url)
            video = dict(video)
            video["url"] = url
            videos_out.append(video)
        tag_out = dict(tag)
        tag_out["videos"] = videos_out
        tag_out["video_count"] = len(videos_out)
        tags_out.append(tag_out)

    return {"tag_count": len(tags_out), "tags": tags_out}, removed


def merge_tag_results_into_payload(
    existing: dict,
    results: list[TikTokTagResult],
) -> dict:
    """Merge new scrape results into existing raw JSON, deduping by video URL."""
    merged, _ = dedupe_raw_payload(existing)
    by_tag = {tag.get("tag"): tag for tag in merged.get("tags") or []}
    seen_urls = {
        _normalize_video_url(video.get("url") or "")
        for tag in merged.get("tags") or []
        for video in tag.get("videos") or []
        if video.get("url")
    }

    for result in results:
        tag_entry = by_tag.get(result.tag)
        if tag_entry is None:
            tag_entry = {
                "tag": result.tag,
                "tag_url": result.tag_url,
                "scraped_at": result.scraped_at,
                "video_count": 0,
                "videos": [],
            }
            by_tag[result.tag] = tag_entry
            merged["tags"].append(tag_entry)

        tag_entry["tag_url"] = result.tag_url
        tag_entry["scraped_at"] = result.scraped_at
        for video in result.videos:
            url = _normalize_video_url(video.url)
            if url in seen_urls:
                continue
            seen_urls.add(url)
            tag_entry["videos"].append(_video_to_dict(video))
        tag_entry["video_count"] = len(tag_entry["videos"])

    merged["tag_count"] = len(merged["tags"])
    return merged


def tag_results_from_payload(payload: dict) -> list[TikTokTagResult]:
    results: list[TikTokTagResult] = []
    for tag in payload.get("tags") or []:
        videos: list[TikTokVideo] = []
        for video in tag.get("videos") or []:
            comments = [
                TikTokComment(
                    author=comment.get("author") or "unknown",
                    text=comment.get("text") or "",
                    video_url=_normalize_video_url(
                        comment.get("video_url") or video.get("url") or ""
                    ),
                    search_query=comment.get("search_query") or "",
                    scraped_at=float(comment.get("scraped_at") or 0.0),
                )
                for comment in video.get("comments") or []
            ]
            videos.append(
                TikTokVideo(
                    url=_normalize_video_url(video.get("url") or ""),
                    tag=video.get("tag") or tag.get("tag") or "",
                    tag_url=video.get("tag_url") or tag.get("tag_url") or "",
                    author=video.get("author") or "",
                    caption=video.get("caption") or "",
                    like_count=video.get("like_count") or "",
                    comment_count=video.get("comment_count") or "",
                    share_count=video.get("share_count") or "",
                    hashtags=list(video.get("hashtags") or []),
                    comments=comments,
                    scraped_at=float(video.get("scraped_at") or 0.0),
                )
            )
        results.append(
            TikTokTagResult(
                tag=tag.get("tag") or "",
                tag_url=tag.get("tag_url") or "",
                videos=videos,
                scraped_at=float(tag.get("scraped_at") or 0.0),
            )
        )
    return results


def _first_text(driver, selectors: tuple[str, ...]) -> str:
    for selector in selectors:
        try:
            text = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
            if text:
                return text
        except Exception:
            continue
    return ""


def _collect_video_links(
    driver,
    limit: int,
    *,
    skip_urls: set[str] | None = None,
) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()
    skip = skip_urls or set()

    for anchor in driver.find_elements(By.CSS_SELECTOR, "a[href*='/video/']"):
        href = anchor.get_attribute("href")
        if not href:
            continue
        href = _normalize_video_url(href)
        if href in seen or href in skip:
            continue
        seen.add(href)
        links.append(href)
        if len(links) >= limit:
            break

    return links


def _scroll_tag_feed(
    driver,
    target_video_count: int,
    *,
    skip_urls: set[str] | None = None,
) -> None:
    last_count = 0
    stagnant_rounds = 0
    # Scroll deeper when skipping known URLs — top posts are often unchanged.
    max_stagnant = 8 if skip_urls else 4

    while stagnant_rounds < max_stagnant:
        current_count = len(
            _collect_video_links(
                driver,
                target_video_count * 5,
                skip_urls=skip_urls,
            )
        )
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
    caption, hashtags = extract_caption(driver)
    like_count = _first_text(driver, ("strong[data-e2e='like-count']",))
    comment_count = _first_text(driver, ("strong[data-e2e='comment-count']",))
    share_count = _first_text(driver, ("strong[data-e2e='share-count']",))

    if caption:
        print(f"    caption={caption[:90]!r}")
    else:
        print("    caption=(empty)")
    if hashtags:
        print(f"    hashtags={', '.join(hashtags[:8])}")

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
        hashtags=hashtags,
        comments=comments,
        scraped_at=scraped_at,
    )


def scrape_tag(
    tag_url: str,
    *,
    max_videos: int = 5,
    max_comments_per_video: int = 25,
    headless: bool = False,
    skip_urls: set[str] | None = None,
) -> TikTokTagResult:
    tag = _tag_name_from_url(tag_url)
    driver = create_tiktok_driver(headless=headless)
    videos: list[TikTokVideo] = []
    skip = {_normalize_video_url(url) for url in (skip_urls or set()) if url}

    try:
        print(f"Opening tag page: {tag_url}")
        if skip:
            print(f"  skipping {len(skip)} already-scraped video URL(s)")
        driver.get(tag_url)
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        dismiss_overlays(driver)

        _scroll_tag_feed(driver, max_videos, skip_urls=skip)
        video_urls = _collect_video_links(driver, max_videos, skip_urls=skip)

        # TikTok intermittently serves a "Something went wrong" shell with no
        # feed; a reload usually recovers it.
        for attempt in range(2):
            if video_urls:
                break
            print(f"No videos rendered for #{tag}, refreshing (attempt {attempt + 1}/2)")
            driver.refresh()
            time.sleep(5)
            dismiss_overlays(driver)
            _scroll_tag_feed(driver, max_videos, skip_urls=skip)
            video_urls = _collect_video_links(driver, max_videos, skip_urls=skip)

        print(f"Found {len(video_urls)} new videos for #{tag}")

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
            skip.add(_normalize_video_url(video_url))
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
    skip_urls: set[str] | None = None,
) -> list[TikTokTagResult]:
    results: list[TikTokTagResult] = []
    skip = {_normalize_video_url(url) for url in (skip_urls or set()) if url}
    for tag_url in tag_urls:
        result = scrape_tag(
            tag_url,
            max_videos=max_videos,
            max_comments_per_video=max_comments_per_video,
            headless=headless,
            skip_urls=skip,
        )
        results.append(result)
        for video in result.videos:
            skip.add(_normalize_video_url(video.url))
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
    existing = load_raw_payload(output_path)
    existing, removed = dedupe_raw_payload(existing)
    if removed:
        print(f"Removed {removed} duplicate video(s) from existing scrape file")

    skip_urls = {
        _normalize_video_url(video.get("url") or "")
        for tag in existing.get("tags") or []
        for video in tag.get("videos") or []
        if video.get("url")
    }

    results = scrape_tags(
        tag_urls,
        max_videos=max_videos,
        max_comments_per_video=max_comments_per_video,
        headless=headless,
        skip_urls=skip_urls,
    )
    payload = merge_tag_results_into_payload(existing, results)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    counts = {
        "tags": len(payload.get("tags") or []),
        "videos": sum(len(tag.get("videos") or []) for tag in payload.get("tags") or []),
        "comments": sum(
            len(video.get("comments") or [])
            for tag in payload.get("tags") or []
            for video in tag.get("videos") or []
        ),
        "new_videos": sum(len(result.videos) for result in results),
    }
    return counts, results
