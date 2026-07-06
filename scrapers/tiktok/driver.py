import undetected_chromedriver as uc


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
