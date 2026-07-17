import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


DISMISS_BUTTON_XPATHS = (
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'got it')]",
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ok')]",
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'not now')]",
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'skip')]",
    "//div[@role='button'][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'got it')]",
    "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'keyboard shortcut')]/ancestor::div[1]//button",
    "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'scroll')]/ancestor::div[.//button][1]//button",
)

DISMISS_SELECTORS = (
    "button[data-e2e='cookie-banner-accept']",
    "button[aria-label='Close']",
    "button[aria-label='close']",
    "[data-e2e='browse-close']",
    "[data-e2e='modal-close-inner-button']",
    "[data-e2e='close-icon']",
)


def _click_if_present(driver, by, value) -> bool:
    try:
        element = driver.find_element(by, value)
        if element.is_displayed():
            element.click()
            time.sleep(0.5)
            return True
    except Exception:
        pass
    return False


def dismiss_overlays(driver, *, rounds: int = 3) -> None:
    """
    Dismiss TikTok onboarding popups (scroll tutorial, cookies, modals).

    TikTok often shows a 'how to scroll' overlay on first video views in a fresh
    browser session. That blocks clicks and hides the comment panel.
    """
    _click_if_present(driver, By.CSS_SELECTOR, "button[aria-label='Close toast']")

    for _ in range(rounds):
        dismissed = False

        for xpath in DISMISS_BUTTON_XPATHS:
            if _click_if_present(driver, By.XPATH, xpath):
                dismissed = True

        for selector in DISMISS_SELECTORS:
            if _click_if_present(driver, By.CSS_SELECTOR, selector):
                dismissed = True

        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.3)
        except Exception:
            pass

        if not dismissed:
            break

        time.sleep(0.5)


def open_comments_panel(driver) -> bool:
    """Open the comments side panel on a TikTok video page."""
    _click_if_present(driver, By.CSS_SELECTOR, "button[aria-label='Close toast']")
    dismiss_overlays(driver)

    # Login / signup walls block the comments panel entirely.
    try:
        body_text = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
        if "log in to" in body_text or "log in to comment" in body_text:
            return False
    except Exception:
        pass

    locators = (
        (By.XPATH, "//button[contains(@aria-label, 'comments')]"),
        (By.XPATH, "//button[contains(@aria-label, 'Comments')]"),
        (By.XPATH, "//button[contains(@aria-label, 'Read or add comments')]"),
        (By.CSS_SELECTOR, "div[data-e2e='comment-icon']"),
        (By.XPATH, "//*[@data-e2e='comment-icon']"),
        (By.XPATH, "//*[contains(@aria-label, 'comments')]"),
        (By.CSS_SELECTOR, "button[data-e2e='browse-comment']"),
        (By.CSS_SELECTOR, "button[data-e2e='comment-icon']"),
        (By.CSS_SELECTOR, "span[data-e2e='comment-icon']"),
    )
    for by, value in locators:
        try:
            button = driver.find_element(by, value)
            if not button.is_displayed():
                continue
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", button
            )
            time.sleep(0.5)
            try:
                button.click()
            except Exception:
                driver.execute_script("arguments[0].click();", button)
            time.sleep(2)
            return True
        except Exception:
            continue
    return False


def find_comment_container(driver):
    selectors = (
        "div[data-e2e='comment-list']",
        "div[class*='DivCommentListContainer']",
        "div[class*='CommentList']",
    )
    for selector in selectors:
        try:
            container = driver.find_element(By.CSS_SELECTOR, selector)
            if container.is_displayed():
                return container
        except Exception:
            continue
    return None
