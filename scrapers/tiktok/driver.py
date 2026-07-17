import sys

import undetected_chromedriver as uc


def _installed_chrome_major() -> int | None:
    """Detect the major version of the installed Chrome browser.

    undetected_chromedriver otherwise downloads the latest ChromeDriver,
    which fails with SessionNotCreatedException whenever the local Chrome
    is one release behind.
    """
    if sys.platform == "win32":
        import winreg

        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            try:
                with winreg.OpenKey(hive, r"Software\Google\Chrome\BLBeacon") as key:
                    version, _ = winreg.QueryValueEx(key, "version")
                return int(str(version).split(".")[0])
            except OSError:
                continue
    return None


def create_tiktok_driver(*, headless: bool = False) -> uc.Chrome:
    """Create an undetected Chrome driver tuned for TikTok scraping."""
    chrome_major = _installed_chrome_major()

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=en-US")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        # Headless Chrome advertises "HeadlessChrome/<ver>" in its user agent,
        # which TikTok flags immediately ("Something went wrong" shell with no
        # feed data). Present the normal Chrome UA instead.
        major = chrome_major or 149
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{major}.0.0.0 Safari/537.36"
        )

    driver = uc.Chrome(
        options=options,
        use_subprocess=False,
        version_main=chrome_major,
    )
    driver.set_window_size(1920, 1080)
    return driver


def close_tiktok_driver(driver: uc.Chrome) -> None:
    """Quit the driver, swallowing the WinError noise undetected_chromedriver
    sometimes raises when Chrome is already gone."""
    try:
        driver.quit()
    except Exception:  # noqa: BLE001
        pass
