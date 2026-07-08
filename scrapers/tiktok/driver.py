import undetected_chromedriver as uc


def close_tiktok_driver(driver: uc.Chrome | None) -> None:
    """Shut down Chrome without WinError 6 noise from uc.Chrome.__del__ on Windows."""
    if driver is None:
        return
    try:
        driver.quit()
    except OSError:
        pass
    except Exception:
        pass
    # uc.Chrome.__del__ calls quit() again during GC; no-op avoids invalid-handle errors.
    driver.quit = lambda *args, **kwargs: None


def create_tiktok_driver(*, headless: bool = False) -> uc.Chrome:
    """Create an undetected Chrome driver tuned for TikTok scraping."""
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=en-US")

    if headless:
        options.add_argument("--headless=new")

    driver = uc.Chrome(options=options, use_subprocess=False)
    driver.set_window_size(1920, 1080)
    return driver
