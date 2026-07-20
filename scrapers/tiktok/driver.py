"""Chrome driver for TikTok scrapes — persistent profile, desktop Chrome only."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import undetected_chromedriver as uc

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PROFILE_DIR = ROOT / "data" / "chrome" / "tiktok_profile"


class ChromeUnavailableError(RuntimeError):
    """Raised when Google Chrome / ChromeDriver cannot start."""


def default_user_data_dir() -> Path:
    """Persistent Chrome user-data-dir so a one-time TikTok login sticks."""
    override = (os.environ.get("CIVICPULSE_CHROME_PROFILE") or "").strip()
    if override:
        return Path(override)
    return DEFAULT_PROFILE_DIR


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


def create_tiktok_driver(
    *,
    headless: bool = False,
    user_data_dir: Path | str | None = None,
) -> uc.Chrome:
    """Create an undetected Chrome driver tuned for TikTok scraping.

    Uses a persistent ``user-data-dir`` (default ``data/chrome/tiktok_profile``)
    so cookies / login survive between runs. Prefer headed mode on a desktop;
    headless TikTok on servers is unreliable (login walls, empty feeds).
    """
    if headless:
        print(
            "warning: TikTok headless mode is unreliable (login walls / empty feeds). "
            "Prefer a headed desktop scrape with the persistent Chrome profile. "
            "See docs/TIKTOK_SCRAPE.md."
        )

    chrome_major = _installed_chrome_major()
    profile_dir = Path(user_data_dir) if user_data_dir else default_user_data_dir()
    try:
        profile_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ChromeUnavailableError(
            f"Cannot create Chrome profile directory at {profile_dir}: {exc}"
        ) from exc

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=en-US")
    options.add_argument(f"--user-data-dir={profile_dir.resolve()}")
    options.add_argument("--profile-directory=Default")

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

    try:
        driver = uc.Chrome(
            options=options,
            use_subprocess=False,
            version_main=chrome_major,
        )
    except Exception as exc:  # noqa: BLE001
        raise ChromeUnavailableError(
            "Chrome is not available or ChromeDriver failed to start. "
            "Install Google Chrome on this desktop and retry "
            "(TikTok scrape is not supported headless on a server). "
            f"Profile: {profile_dir}. Detail: {exc}"
        ) from exc

    driver.set_window_size(1920, 1080)
    return driver


def close_tiktok_driver(driver) -> None:
    """Quit the Chrome session; ignore cleanup errors from undetected-chromedriver."""
    if driver is None:
        return
    try:
        driver.quit()
    except OSError:
        pass
    except Exception:  # noqa: BLE001
        pass
    # Prevent undetected_chromedriver.__del__ from calling quit() again on Windows.
    try:
        object.__setattr__(driver, "quit", lambda: None)
    except Exception:  # noqa: BLE001
        pass
