"""
Seed a demo-ready database: import signals + create a research with archive hits.

Usage:
    python scripts/seed_demo.py          # SQLite (DATA_BACKEND=sqlite)
    python scripts/seed_demo.py --check  # just report counts, no changes
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo database.")
    parser.add_argument("--check", action="store_true", help="Report counts only.")
    args = parser.parse_args()

    from backend.app import create_app

    app = create_app()
    with app.app_context():
        from backend.store import get_research_store, get_signal_store
        from backend.research_match import match_signals

        sig_store = get_signal_store()
        signals = sig_store.list_signals()

        if args.check:
            print(f"Signals in DB: {len(signals)}")
            res_store = get_research_store()
            researches = res_store.list_researches()
            print(f"Researches: {len(researches)}")
            for r in researches:
                print(f"  [{r['status']}] {r['title']} — {r.get('hit_count', 0)} hits")
            return

        if len(signals) == 0:
            print("No signals in DB. Run import first:")
            print("  py scripts/import_signals.py")
            print("  (or py scripts/import_signals_firestore.py for Firestore)")
            sys.exit(1)

        print(f"Found {len(signals)} signals in DB.")

        res_store = get_research_store()

        demos = [
            {
                "title": "Housing affordability in Irvine",
                "topic": "What residents say about rent, mortgages, and cost of living",
                "keywords": ["rent", "housing prices", "lease", "affordable", "mortgage"],
                "categories": ["housing"],
                "extract": ["sentiment", "clustering", "policy"],
            },
            {
                "title": "Pothole and road complaints",
                "topic": "Resident reports of potholes, road damage, and street conditions",
                "keywords": ["pothole", "road damage", "street repair", "pavement"],
                "categories": ["potholes"],
                "extract": ["sentiment", "demographics"],
            },
            {
                "title": "Public safety concerns after dark",
                "topic": "How safe residents feel at night — streetlights, patrols, incidents",
                "keywords": ["streetlight", "unsafe", "patrol", "night safety"],
                "categories": ["public_safety", "violent_crime"],
                "extract": ["sentiment", "clustering", "policy", "demographics"],
            },
        ]

        created_count = 0
        for demo in demos:
            existing = res_store.list_researches()
            if any(r["title"] == demo["title"] for r in existing):
                print(f"  Skip (exists): {demo['title']}")
                continue

            research = res_store.create_research(
                title=demo["title"],
                topic=demo["topic"],
                keywords=demo["keywords"],
                categories=demo["categories"],
                extract=demo.get("extract", []),
                notes="Demo research — seeded by scripts/seed_demo.py",
            )
            rid = research["id"]

            matched = match_signals(
                signals, demo["categories"], demo["keywords"],
            )
            if matched:
                res_store.replace_hits(rid, matched)
                res_store.update_research(rid, status="active")
                print(f"  Created: {demo['title']} — {len(matched)} hits")
            else:
                print(f"  Created: {demo['title']} — 0 hits (no matches)")
            created_count += 1

        if created_count == 0:
            print("All demo researches already exist.")
        else:
            print(f"\nSeeded {created_count} demo researches.")

        print("\nDone. Start the server and visit /research.html")


if __name__ == "__main__":
    main()
