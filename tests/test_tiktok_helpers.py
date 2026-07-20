"""Unit tests for TikTok UI helpers (no Selenium browser)."""

from scrapers.tiktok.driver import DEFAULT_PROFILE_DIR, default_user_data_dir
from scrapers.tiktok.ui import (
    BLOCKING_LOGIN_PHRASES,
    LOGIN_WALL_PHRASES,
    TikTokLoginWallError,
    is_login_wall,
)


class _FakeBody:
    def __init__(self, text: str):
        self.text = text


class _FakeElement:
    def __init__(self, text: str, displayed: bool = True):
        self.text = text
        self._displayed = displayed

    def is_displayed(self):
        return self._displayed


class _FakeDriver:
    def __init__(self, text: str, *, modals=None, url="https://www.tiktok.com/"):
        self._text = text
        self._modals = modals or []
        self.current_url = url

    def find_element(self, by, value):
        return _FakeBody(self._text)

    def find_elements(self, by, value):
        return list(self._modals)


def test_default_profile_dir_under_data_chrome(monkeypatch):
    monkeypatch.delenv("CIVICPULSE_CHROME_PROFILE", raising=False)
    path = default_user_data_dir()
    assert path == DEFAULT_PROFILE_DIR
    assert path.as_posix().endswith("data/chrome/tiktok_profile")


def test_chrome_profile_env_override(monkeypatch, tmp_path):
    custom = tmp_path / "my_profile"
    monkeypatch.setenv("CIVICPULSE_CHROME_PROFILE", str(custom))
    assert default_user_data_dir() == custom


def test_header_log_in_is_not_a_wall():
    """Guest pages always show Log in / Sign up — that must not abort scrapes."""
    driver = _FakeDriver(
        "Log in  Sign up  For You  Following  "
        "Nice pothole video from Irvine residents"
    )
    assert is_login_wall(driver) is False


def test_is_login_wall_detects_blocking_comment_gate():
    driver = _FakeDriver("Please log in to see comments on this video")
    assert is_login_wall(driver) is True


def test_is_login_wall_detects_you_need_to_login():
    driver = _FakeDriver("You need to log in to continue watching")
    assert is_login_wall(driver) is True


def test_is_login_wall_detects_visible_login_modal():
    modal = _FakeElement("Log in to TikTok\nContinue with Google\nContinue with Facebook")
    driver = _FakeDriver("video caption text", modals=[modal])
    assert is_login_wall(driver) is True


def test_is_login_wall_negative():
    driver = _FakeDriver("Nice pothole video from Irvine residents")
    assert is_login_wall(driver) is False


def test_login_wall_phrases_nonempty():
    assert len(BLOCKING_LOGIN_PHRASES) >= 2
    assert len(LOGIN_WALL_PHRASES) >= 3
    assert isinstance(TikTokLoginWallError("x"), RuntimeError)
