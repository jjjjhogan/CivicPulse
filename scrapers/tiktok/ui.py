"""TikTok DOM helpers: overlays, optional login gate, comments panel.

Designed for anonymous (no-login) scraping. TikTok always shows Log in / Sign up
in the header for guests — that alone is not a wall. A dedicated account is
only needed if comments stay unreachable after overlays are dismissed.
"""

from __future__ import annotations

import time

from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class TikTokLoginWallError(RuntimeError):
    """Raised only when a hard login gate clearly blocks the entire scrape.

    Prefer soft warnings + empty comments for per-video failures; anonymous
    browsing usually still works.
    """


# Conservative: only clear onboarding / cookie / soft-dismiss CTAs.
# Do NOT match bare "ok" / "accept" / generic Close — those close video chrome
# or click the wrong control and leave you on a login interstitial.
DISMISS_BUTTON_XPATHS = (
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'got it')]",
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'not now')]",
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'skip')]",
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'maybe later')]",
    "//div[@role='button'][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'got it')]",
    "//div[@role='button'][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'not now')]",
    "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'keyboard shortcut')]/ancestor::div[1]//button",
)

COOKIE_SELECTORS = (
    "button[data-e2e='cookie-banner-accept']",
    "button[aria-label='Close toast']",
)

# Close controls used only when a login modal is confirmed visible.
LOGIN_DISMISS_SELECTORS = (
    "[data-e2e='modal-close-inner-button']",
    "[data-e2e='close-icon']",
    "div[data-e2e='modal-close']",
    "button[data-e2e='close-button']",
    "button[aria-label='Close']",
    "button[aria-label='close']",
)

# Phrases that mean comments are gated — not the always-visible header "Log in".
BLOCKING_LOGIN_PHRASES = (
    "log in to see comments",
    "log in to comment",
    "log in to see this content",
    "you need to log in",
    "you need to login",
    "login to continue",
    "log in to continue",
)

LOGIN_WALL_PHRASES = BLOCKING_LOGIN_PHRASES + (
    "log in to tiktok",
    "log in to follow",
    "sign up for an account",
    "continue with google",
    "continue with facebook",
    "use phone / email / username",
)

# Avoid broad div[role='dialog'] — guest pages have many dialogs.
LOGIN_MODAL_SELECTORS = (
    "[data-e2e='login-modal']",
    "[data-e2e='modal-login']",
    "div[class*='DivLoginContainer']",
    "div[class*='DivLoginModal']",
    "div[class*='DivLoginPortalContainer']",
    "div[class*='login-modal']",
)


def window_is_alive(driver) -> bool:
    try:
        _ = driver.current_url
        return True
    except (NoSuchWindowException, WebDriverException):
        return False


def _click_if_present(driver, by, value) -> bool:
    if not window_is_alive(driver):
        return False
    try:
        element = driver.find_element(by, value)
        if element.is_displayed():
            element.click()
            time.sleep(0.4)
            return True
    except Exception:
        pass
    return False


def page_body_text(driver) -> str:
    if not window_is_alive(driver):
        return ""
    try:
        return (driver.find_element(By.TAG_NAME, "body").text or "").lower()
    except Exception:
        return ""


def _visible_login_modal(driver):
    """Return a visible login-ish dialog element, or None."""
    if not window_is_alive(driver):
        return None
    for selector in LOGIN_MODAL_SELECTORS:
        try:
            for element in driver.find_elements(By.CSS_SELECTOR, selector):
                if not element.is_displayed():
                    continue
                text = (element.text or "").lower()
                if any(
                    phrase in text
                    for phrase in (
                        "continue with",
                        "use phone",
                        "log in to comment",
                        "log in to see comments",
                        "you need to log",
                        "log in to tiktok",
                        "sign up",
                    )
                ):
                    return element
        except Exception:
            continue
    return None


def is_login_wall(driver) -> bool:
    """True only when a blocking login gate likely prevents reading comments.

    Guest pages always include Log in / Sign up chrome — ignore that.
    """
    body = page_body_text(driver)
    if body and any(phrase in body for phrase in BLOCKING_LOGIN_PHRASES):
        return True
    return _visible_login_modal(driver) is not None


def warn_login_hint(context: str = "TikTok") -> None:
    print(
        f"  hint ({context}): login interstitial still visible after dismiss. "
        "Try Esc / Not now in the Chrome window, then re-run. "
        "Account login is optional — see docs/TIKTOK_SCRAPE.md."
    )


def raise_if_login_wall(driver, *, context: str = "TikTok") -> None:
    """Hard fail — rarely used. Prefer warn + continue for no-login scrapes."""
    if is_login_wall(driver):
        raise TikTokLoginWallError(
            f"{context}: TikTok login wall is blocking this page. "
            "Anonymous browsing usually works — dismiss the popup and retry. "
            "Only log in (data/chrome/tiktok_profile) if comments stay blocked. "
            "See docs/TIKTOK_SCRAPE.md."
        )


def dismiss_login_interstitial(driver) -> bool:
    """Best-effort close of a login popup without nuking the video page."""
    if not window_is_alive(driver):
        return False

    dismissed = False
    for xpath in (
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'not now')]",
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'maybe later')]",
        "//div[@role='button'][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'not now')]",
    ):
        if _click_if_present(driver, By.XPATH, xpath):
            dismissed = True

    modal = _visible_login_modal(driver)
    if modal is not None or is_login_wall(driver):
        for selector in LOGIN_DISMISS_SELECTORS:
            if _click_if_present(driver, By.CSS_SELECTOR, selector):
                dismissed = True
                break
        else:
            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(0.4)
                dismissed = True
            except Exception:
                pass

    return dismissed


def dismiss_overlays(driver, *, rounds: int = 3) -> None:
    """
    Dismiss TikTok onboarding / cookie toasts carefully.

    Avoids generic Close / Esc spam that can close the video or leave a
    login interstitial stuck on screen.
    """
    if not window_is_alive(driver):
        return

    for selector in COOKIE_SELECTORS:
        _click_if_present(driver, By.CSS_SELECTOR, selector)

    for _ in range(rounds):
        dismissed = False

        for xpath in DISMISS_BUTTON_XPATHS:
            if _click_if_present(driver, By.XPATH, xpath):
                dismissed = True

        if dismiss_login_interstitial(driver):
            dismissed = True

        if not dismissed:
            break
        time.sleep(0.4)


def comments_panel_open(driver) -> bool:
    return find_comment_container(driver) is not None


def close_comments_panel(driver) -> None:
    """Best-effort dismiss of an open comments drawer (not the whole video)."""
    if not window_is_alive(driver):
        return
    # Prefer TikTok's comment-drawer close — avoid browse-close (leaves video).
    for selector in (
        "[data-e2e='comment-close']",
        "button[data-e2e='close-icon']",
    ):
        if _click_if_present(driver, By.CSS_SELECTOR, selector):
            time.sleep(0.4)
            return
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.3)
    except Exception:
        pass


def open_comments_panel(driver, *, retries: int = 2) -> bool:
    """Open the comments side panel on a TikTok video page.

    Returns True if the panel appears (or was already open). Never raises for
    guest "Log in" chrome — anonymous scrapes are the default path.
    """
    if not window_is_alive(driver):
        return False

    dismiss_overlays(driver)
    dismiss_login_interstitial(driver)

    if comments_panel_open(driver):
        return True

    # Prefer explicit comment controls; avoid bare comment-count (can open login).
    locators = (
        (By.CSS_SELECTOR, "button[data-e2e='browse-comment']"),
        (By.CSS_SELECTOR, "button[data-e2e='comment-icon']"),
        (By.XPATH, "//button[contains(@aria-label, 'Read or add comments')]"),
        (By.XPATH, "//button[contains(@aria-label, 'comments') or contains(@aria-label, 'Comments')]"),
        (By.CSS_SELECTOR, "div[data-e2e='comment-icon']"),
        (By.CSS_SELECTOR, "span[data-e2e='comment-icon']"),
        (By.XPATH, "//*[@data-e2e='comment-icon']"),
    )

    for attempt in range(retries + 1):
        if not window_is_alive(driver):
            return False
        if attempt > 0:
            dismiss_overlays(driver)
            dismiss_login_interstitial(driver)
            time.sleep(0.6)

        clicked = False
        for by, value in locators:
            try:
                button = driver.find_element(by, value)
                if not button.is_displayed():
                    continue
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", button
                )
                time.sleep(0.3)
                try:
                    button.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", button)
                clicked = True
                time.sleep(1.2)
                break
            except Exception:
                continue

        if not clicked:
            continue

        for _ in range(8):
            if not window_is_alive(driver):
                return False
            if comments_panel_open(driver):
                return True
            # Comment click often opens a login modal for bots — dismiss, don't Escape-spam.
            if is_login_wall(driver) or _visible_login_modal(driver) is not None:
                dismiss_login_interstitial(driver)
            time.sleep(0.4)

    return comments_panel_open(driver) if window_is_alive(driver) else False


def find_comment_container(driver):
    if not window_is_alive(driver):
        return None
    selectors = (
        "div[data-e2e='comment-list']",
        "div[class*='DivCommentListContainer']",
        "div[class*='CommentList']",
        "div[class*='DivCommentMain']",
    )
    for selector in selectors:
        try:
            container = driver.find_element(By.CSS_SELECTOR, selector)
            if container.is_displayed():
                return container
        except Exception:
            continue
    return None
