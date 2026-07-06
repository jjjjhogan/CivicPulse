import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.tiktok.driver import create_tiktok_driver
from scrapers.tiktok.ui import dismiss_overlays, open_comments_panel

URL = "https://www.tiktok.com/@buildsbyb/video/7657282877155069198"

if __name__ == "__main__":
    driver = create_tiktok_driver()
    try:
        driver.get(URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)
        print("title:", driver.title)
        print("url:", driver.current_url)

        commentish = driver.find_elements(
            By.XPATH,
            "//*[contains(translate(@aria-label, 'COMMENT', 'comment'), 'comment') or contains(@data-e2e, 'comment')]",
        )
        print(f"comment-related elements: {len(commentish)}")
        for el in commentish[:15]:
            print(
                f"  <{el.tag_name}> aria={el.get_attribute('aria-label')!r} "
                f"e2e={el.get_attribute('data-e2e')!r} text={el.text[:40]!r}"
            )

        dismiss_overlays(driver)
        opened = open_comments_panel(driver)
        print("opened comments panel:", opened)
        time.sleep(3)

        for selector in (
            "div[data-e2e='comment-level-1']",
            "div[data-e2e='comment-list']",
            "span[data-e2e='comment-level-1']",
            "a[data-e2e='comment-username']",
        ):
            els = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"{selector}: {len(els)}")
            if els and "comment-level-1" in selector and "span" in selector:
                print(f"  sample: {els[0].text[:80]!r}")

        time.sleep(8)
    finally:
        driver.quit()
