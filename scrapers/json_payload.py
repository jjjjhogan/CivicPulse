"""Lenient parsing for Reddit / Twitter import pastes.

Accepts:
  - Normal JSON objects
  - JSON missing outer `{` `}` braces
  - Leading UI icons from browser DevTools dumps
  - DevTools tree copies with `{N}` / `[N]` size markers, e.g.::

        ▾{4}
        blocked: false
        query: "irvine"
        items: [1]
        ▾0: {3}
        id: "abc"
        title: "Hello"
        score: 1
        itemCount: 1
"""

from __future__ import annotations

import json
import re
from typing import Any

_LEADING_ICONS = frozenset("▾▶▼►▸▹▽△•·")
_SHOW_MORE = re.compile(r"…show\s+\d+\s+more", re.IGNORECASE)
_OBJ_MARK = re.compile(r"^\{\d+\}")
_ARR_MARK = re.compile(r"^\[\d+\]")
_KEY = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*:")
_INDEX_KEY = re.compile(r"^(?P<key>\d+)\s*:")


class ImportPayloadError(ValueError):
    """Raised when pasted import text cannot be turned into a JSON object."""


def parse_import_payload(raw: Any) -> dict:
    """Parse an import payload from a dict, JSON string, or DevTools dump."""
    if raw is None:
        raise ImportPayloadError("JSON payload is required.")
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        raise ImportPayloadError("JSON payload must be an object or JSON string.")

    text = raw.strip()
    if not text:
        raise ImportPayloadError("JSON payload is empty.")

    try:
        return _require_object(json.loads(text))
    except json.JSONDecodeError:
        pass

    cleaned = _strip_noise(text)

    for candidate in _json_candidates(cleaned):
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    try:
        return _require_object(_parse_devtools_dump(cleaned))
    except ImportPayloadError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ImportPayloadError(
            "Could not parse paste as JSON. Tip: in DevTools right-click the "
            f"object → Copy object, or upload a .json file. ({exc})"
        ) from exc


def _require_object(value: Any) -> dict:
    if not isinstance(value, dict):
        raise ImportPayloadError("JSON payload must be an object.")
    return value


def _strip_noise(text: str) -> str:
    text = text.lstrip("\ufeff")
    while text and (text[0] in _LEADING_ICONS or text[0].isspace()):
        text = text[1:]
    text = "".join(ch for ch in text if ch not in _LEADING_ICONS)
    text = _SHOW_MORE.sub("", text)
    return text.strip()


def _json_candidates(text: str) -> list[str]:
    candidates = [text]
    if not text.startswith(("{", "[")):
        candidates.append("{" + text + "}")
    stripped_size = re.sub(r"^\{(\d+)\}", "{", text, count=1)
    if stripped_size != text:
        candidates.append(stripped_size)
        if not stripped_size.startswith("{"):
            candidates.append("{" + stripped_size + "}")
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end > start:
            candidates.append(text[start : end + 1])
    seen: set[str] = set()
    out: list[str] = []
    for item in candidates:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _parse_devtools_dump(text: str) -> dict:
    src = text.strip()
    if not src:
        raise ImportPayloadError("DevTools dump is empty.")

    parser = _DevToolsParser(src)
    if _OBJ_MARK.match(src):
        value = parser.parse_value()
    else:
        value = parser.parse_object(count=None)
    parser.skip_ws()
    if not isinstance(value, dict):
        raise ImportPayloadError("DevTools dump root must be an object.")
    # Leftover text is OK when we already recovered the scrape payload —
    # Chrome copies are often truncated mid-tree after the useful fields.
    if parser.pos < len(parser.text):
        has_rows = bool(value.get("items") or value.get("tweets") or value.get("scrapes"))
        if not has_rows:
            trailing = parser.text[parser.pos : parser.pos + 60]
            raise ImportPayloadError(
                f"Unexpected trailing text in DevTools dump: {trailing!r}"
            )
    return value

class _DevToolsParser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def skip_ws(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def remaining(self) -> str:
        return self.text[self.pos :]

    def parse_value(self) -> Any:
        self.skip_ws()
        rest = self.remaining()
        if not rest:
            raise ImportPayloadError("Unexpected end of DevTools dump.")

        obj_mark = _OBJ_MARK.match(rest)
        if obj_mark:
            count = int(obj_mark.group(0)[1:-1])
            self.pos += obj_mark.end()
            return self.parse_object(count=count)

        arr_mark = _ARR_MARK.match(rest)
        if arr_mark:
            count = int(arr_mark.group(0)[1:-1])
            self.pos += arr_mark.end()
            return self.parse_array(count=count)

        if rest.startswith('"'):
            return self.parse_string()

        return self.parse_scalar()

    def parse_object(self, *, count: int | None) -> dict:
        result: dict[str, Any] = {}
        read = 0
        while self.pos < len(self.text) and (count is None or read < count):
            self.skip_ws()
            if self.pos >= len(self.text):
                break
            key_match = _KEY.match(self.remaining())
            if not key_match:
                break
            key = key_match.group("key")
            self.pos += key_match.end()
            try:
                result[key] = self.parse_value()
            except ImportPayloadError:
                # Truncated / messy value — keep properties we already have.
                break
            read += 1
        # DevTools `{N}` counts are often wrong after a messy copy (inner
        # quotes, "show more" chrome). Prefer a partial object over failing.
        return result

    def parse_array(self, *, count: int) -> list:
        result: list[Any] = []
        for index in range(count):
            self.skip_ws()
            if self.pos >= len(self.text):
                break
            # Sibling property after the array (e.g. itemCount:) means we're done.
            idx_match = _INDEX_KEY.match(self.remaining())
            named = _KEY.match(self.remaining())
            if named and not idx_match:
                break
            if idx_match and idx_match.group("key") == str(index):
                self.pos += idx_match.end()
            try:
                result.append(self.parse_value())
            except ImportPayloadError:
                break
        return result

    def parse_string(self) -> str:
        """Read a "…" value, tolerating unescaped quotes inside the text.

        DevTools copies of Reddit previewText often include raw quotes like
        ``called it the "Circles" channel``. Close at the quote that sits
        right before the next property key / array index.
        """
        assert self.remaining().startswith('"')
        self.pos += 1
        i = self.pos
        closer: int | None = None
        while i < len(self.text):
            ch = self.text[i]
            if ch == "\\" and i + 1 < len(self.text):
                i += 2
                continue
            if ch == '"':
                after = self.text[i + 1 :].lstrip()
                if (
                    not after
                    or _KEY.match(after)
                    or _INDEX_KEY.match(after)
                ):
                    closer = i
                    break
                # Inner quote — keep scanning.
            i += 1
        if closer is None:
            # No clean boundary; take through EOF (better than failing the import).
            value = self.text[self.pos :]
            self.pos = len(self.text)
            return _unescape_devtools_string(value)
        value = self.text[self.pos : closer]
        self.pos = closer + 1
        return _unescape_devtools_string(value)

    def parse_scalar(self) -> Any:
        rest = self.remaining()
        # Prefer explicit literals / numbers even when glued to the next key:
        # `falseListingType:` or `false\nlistingType:`.
        lit = re.match(r"^(null|true|false)", rest)
        if lit:
            token = lit.group(1)
            self.pos += lit.end()
            return {"null": None, "true": True, "false": False}[token]

        num = re.match(r"^(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)", rest)
        if num:
            token = num.group(1)
            # Don't swallow digits that are an array index (`0:`).
            after = rest[num.end() :]
            if after.startswith(":"):
                raise ImportPayloadError(
                    f"Unexpected index-like token while reading scalar near {rest[:40]!r}"
                )
            self.pos += num.end()
            if re.fullmatch(r"-?\d+", token):
                return int(token)
            return float(token)

        # Bareword until next key boundary.
        boundary = re.search(r"[A-Za-z_][A-Za-z0-9_]*\s*:", rest)
        if boundary and boundary.start() > 0:
            token = rest[: boundary.start()].strip()
            self.pos += boundary.start()
            return token

        token = rest.strip()
        self.pos = len(self.text)
        return token


def _unescape_devtools_string(value: str) -> str:
    return (
        value.replace(r"\"", '"')
        .replace(r"\n", "\n")
        .replace(r"\t", "\t")
        .replace(r"\\", "\\")
    )