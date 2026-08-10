"""
Bootstrap data/pool/*.json from signals + *_all.json.

Usage:
    python scripts/bootstrap_pool.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.pool import bootstrap_ponds  # noqa: E402


def main() -> None:
    totals = bootstrap_ponds()
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
