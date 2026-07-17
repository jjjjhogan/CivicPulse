"""Extract TikTok video captions and hashtags from a loaded Selenium page."""

from __future__ import annotations

import json
import re
import time

from selenium.webdriver.common.by import By

DESC_SELECTORS = (
    "div[data-e2e='browse-video-desc']",
    "div[data-e2e='video-desc']",
    "h1[data-e2e='browse-video-desc']",
    "span[data-e2e='browse-video-desc']",
    "div[data-e2e='new-desc-span']",
    "div[class*='VideoDescription']",
    "div[class*='DescText']",
    "h1[data-e2e='video-desc']",
)

MORE_BUTTON_XPATHS = (
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'more')]",
    "//span[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'more')]",
    "//*[@data-e2e='video-desc']//*[contains(translate(., 'MORE', 'more'), 'more')]",
)

# TikTok sometimes surfaces analytics / route tokens instead of the real caption.
_JUNK_CAPTION_RE = re.compile(
    r"^(pc_web_|webapp\.|tiktok://|https?://)",
    re.IGNORECASE,
)
_JUNK_CAPTIONS = {
    "more",
    "less",
    "follow",
    "log in",
    "login",
    "sign up",
}


def is_plausible_caption(text: str) -> bool:
    text = (text or "").strip()
    if len(text) < 2:
        return False
    if text.lower() in _JUNK_CAPTIONS:
        return False
    if _JUNK_CAPTION_RE.search(text):
        return False
    # Internal tokens like pc_web_explorePage_all (no spaces, camel/snake mix).
    if " " not in text and "_" in text and not text.startswith("#"):
        return False
    return True


def _visible_text(element) -> str:
    try:
        text = (element.text or "").strip()
        if text:
            return text
    except Exception:
        pass
    try:
        return (element.get_attribute("textContent") or "").strip()
    except Exception:
        return ""


def _expand_description(driver) -> None:
    for xpath in MORE_BUTTON_XPATHS:
        try:
            for button in driver.find_elements(By.XPATH, xpath):
                if not button.is_displayed():
                    continue
                label = (button.text or "").strip().lower()
                if label and "more" not in label:
                    continue
                try:
                    button.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", button)
                time.sleep(0.4)
                return
        except Exception:
            continue


def _caption_from_dom(driver) -> str:
    _expand_description(driver)
    for selector in DESC_SELECTORS:
        try:
            for element in driver.find_elements(By.CSS_SELECTOR, selector):
                text = _visible_text(element)
                if is_plausible_caption(text):
                    return text
        except Exception:
            continue
    return ""


def _caption_from_og(driver) -> str:
    try:
        meta = driver.find_element(By.CSS_SELECTOR, 'meta[property="og:description"]')
        content = (meta.get_attribute("content") or "").strip()
        if is_plausible_caption(content):
            return content
    except Exception:
        pass
    try:
        meta = driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
        content = (meta.get_attribute("content") or "").strip()
        if is_plausible_caption(content):
            return content
    except Exception:
        pass
    return ""


def _walk_for_desc(node, depth: int = 0):
    if depth > 8 or not isinstance(node, dict):
        return ""
    for key in ("desc", "description", "text", "title"):
        value = node.get(key)
        if isinstance(value, str) and is_plausible_caption(value) and key != "title":
            return value.strip()
    for value in node.values():
        if isinstance(value, dict):
            found = _walk_for_desc(value, depth + 1)
            if found:
                return found
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    found = _walk_for_desc(item, depth + 1)
                    if found:
                        return found
    return ""


def _caption_from_page_json(driver) -> str:
    scripts = (
        "script#__UNIVERSAL_DATA_FOR_REHYDRATION__",
        "script#SIGI_STATE",
        "script#__NEXT_DATA__",
    )
    for selector in scripts:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            raw = element.get_attribute("textContent") or element.get_attribute("innerHTML")
            if not raw:
                continue
            payload = json.loads(raw)
            found = _walk_for_desc(payload)
            if found:
                return found
        except Exception:
            continue
    return ""


def extract_hashtags(driver, caption: str = "") -> list[str]:
    tags: list[str] = []
    seen: set[str] = set()

    for match in re.findall(r"#([A-Za-z0-9_]+)", caption or ""):
        key = match.lower()
        if key not in seen:
            seen.add(key)
            tags.append(match)

    try:
        anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/tag/']")
    except Exception:
        anchors = []

    for anchor in anchors:
        try:
            href = anchor.get_attribute("href") or ""
            text = (anchor.text or "").strip().lstrip("#")
            if "/tag/" in href:
                slug = href.rstrip("/").split("/tag/", 1)[-1].split("?", 1)[0]
                text = text or slug
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            # Skip huge unrelated tag clouds far down the page.
            if len(seen) >= 25:
                break
            seen.add(key)
            tags.append(text)
        except Exception:
            continue

    return tags


def extract_caption(driver) -> tuple[str, list[str]]:
    """
    Return (caption_text, hashtags).

    Tries visible description first, then og/meta and embedded JSON which
    often still contain the caption when DOM text is empty.
    """
    caption = _caption_from_dom(driver)
    if not caption:
        caption = _caption_from_og(driver)
    if not caption:
        caption = _caption_from_page_json(driver)
    if caption and not is_plausible_caption(caption):
        caption = ""

    hashtags = extract_hashtags(driver, caption)
    if hashtags and caption:
        missing = [f"#{tag}" for tag in hashtags if f"#{tag.lower()}" not in caption.lower()]
        if missing:
            caption = f"{caption} {' '.join(missing)}".strip()
    elif hashtags and not caption:
        caption = " ".join(f"#{tag}" for tag in hashtags)

    return caption.strip(), hashtags
