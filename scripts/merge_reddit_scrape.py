"""
Merge Reddit scrape batches into data/raw/reddit_scrape.json.

Usage:
    python scripts/merge_reddit_scrape.py
    python scripts/merge_reddit_scrape.py --from-json path/to/export.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "reddit_scrape.json"
sys.path.insert(0, str(ROOT))

from scripts.seed_reddit_scrape import ITEMS as NEWS_ITEMS  # noqa: E402

IRVINE_ITEMS = [
    {
        "id": "1uqoc80",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "robyobyobyoby",
        "title": "Do Irvine Residents Feel Safer with Flock Cameras everywhere?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uqoc80/do_irvine_residents_feel_safer_with_flock_cameras/",
        "url": "https://old.reddit.com/r/irvine/comments/1uqoc80/do_irvine_residents_feel_safer_with_flock_cameras/",
        "createdAt": "2026-07-08T10:06:59+00:00",
        "score": 50,
        "commentCount": 62,
        "previewText": (
            "Are the security risks, constant monitoring, the fact that a private corporation is in "
            "control of the data as you cant own a flock device only rent it, and this information "
            "being used for issues unrelated to motor vehicles worth it? Just check the logs for "
            "these cameras to see how many requests are made for immigration instead of actual crimes."
        ),
    },
    {
        "id": "1uqilbd",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "Irvinepd",
        "title": "Missing Person!",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uqilbd/missing_person/",
        "url": "https://old.reddit.com/r/irvine/comments/1uqilbd/missing_person/",
        "createdAt": "2026-07-08T04:41:57+00:00",
        "score": 92,
        "commentCount": 7,
        "previewText": (
            "UPDATE - Found and home safe. Thank you, everyone! We need help finding Amy Harchol, "
            "a 67-year-old woman. She walked away from her home near Harcum Ln. and Saginaw Dr. "
            "this morning around 9:30 a.m. Please call 9-1-1 if you see Amy."
        ),
    },
    {
        "id": "1uqhn8m",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "loneMnM",
        "title": "Pregnancy journey doctor recommendations",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uqhn8m/pregnancy_journey_doctor_recommendations/",
        "url": "https://old.reddit.com/r/irvine/comments/1uqhn8m/pregnancy_journey_doctor_recommendations/",
        "createdAt": "2026-07-08T03:54:06+00:00",
        "score": 2,
        "commentCount": 3,
        "previewText": (
            "Wife and I are blessed with our first born but the birth was very difficult. "
            "Every pregnancy since then has been a miscarriage. Any good doctor or IVF recommendations?"
        ),
    },
    {
        "id": "1uqb87z",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "Salty-Employment6229",
        "title": "Altair in the news again?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uqb87z/altair_in_the_news_again/",
        "url": "https://old.reddit.com/r/irvine/comments/1uqb87z/altair_in_the_news_again/",
        "createdAt": "2026-07-07T23:07:36+00:00",
        "score": 43,
        "commentCount": 24,
        "previewText": "Three helicopters hovering in place over the community",
    },
    {
        "id": "1uqam9g",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "capriciousguacamole",
        "title": "Our lovely new slurry seal",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uqam9g/our_lovely_new_slurry_seal/",
        "url": "https://old.reddit.com/r/irvine/comments/1uqam9g/our_lovely_new_slurry_seal/",
        "createdAt": "2026-07-07T22:42:56+00:00",
        "score": 16,
        "commentCount": 15,
        "previewText": (
            "How is the slurry seal from last week already ruined? Is it melting from the heat? "
            "Did it get wet? Did they remove the cones too soon? It still feels soft."
        ),
    },
    {
        "id": "1upncbx",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "hydroblastii2",
        "title": "Best food spots around Irvine Valley College?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1upncbx/best_food_spots_around_irvine_valley_college/",
        "url": "https://old.reddit.com/r/irvine/comments/1upncbx/best_food_spots_around_irvine_valley_college/",
        "createdAt": "2026-07-07T06:57:07+00:00",
        "score": 29,
        "commentCount": 33,
        "previewText": (
            "I'm currently a new student at IVC taking summer classes. "
            "Do you guys have any recommendations for any good food spots by the area?"
        ),
    },
    {
        "id": "1uplzc4",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "centimetercat8",
        "title": "Affordable cat vet in area?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uplzc4/affordable_cat_vet_in_area/",
        "url": "https://old.reddit.com/r/irvine/comments/1uplzc4/affordable_cat_vet_in_area/",
        "createdAt": "2026-07-07T05:42:27+00:00",
        "score": 8,
        "commentCount": 9,
        "previewText": (
            "Any recs for affordable cat vets in irvine or surrounding area? "
            "Ideally somewhere closer to Irvine or within a 30 min drive."
        ),
    },
    {
        "id": "1upevdi",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "HastenDownTheWind",
        "title": "Beware if Aptive Pest Control Comes to your door for sign up, do not do it.",
        "permalink": "https://old.reddit.com/r/irvine/comments/1upevdi/beware_if_aptive_pest_control_comes_to_your_door/",
        "url": "https://old.reddit.com/r/irvine/comments/1upevdi/beware_if_aptive_pest_control_comes_to_your_door/",
        "createdAt": "2026-07-07T00:05:38+00:00",
        "score": 81,
        "commentCount": 13,
        "previewText": (
            "My elderly parents signed up for Aptive pest control when they came to their door last week. "
            "This company is not accredited and have an average 1.07 Star rating with 739 reviews. "
            "They are scammers. Do not sign up and tell your elderly parents to NOT open the door."
        ),
    },
    {
        "id": "1up3gnk",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "WeatherInternal3409",
        "title": "Espresso machine repair recommendations?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1up3gnk/espresso_machine_repair_recommendations/",
        "url": "https://old.reddit.com/r/irvine/comments/1up3gnk/espresso_machine_repair_recommendations/",
        "createdAt": "2026-07-06T17:07:21+00:00",
        "score": 2,
        "commentCount": 6,
        "previewText": (
            "I was wondering if anyone has recommendations for repair services for home espresso machines."
        ),
    },
    {
        "id": "1up220d",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "Comfortable-Bike9080",
        "title": "School District / Family Move",
        "permalink": "https://old.reddit.com/r/irvine/comments/1up220d/school_district_family_move/",
        "url": "https://old.reddit.com/r/irvine/comments/1up220d/school_district_family_move/",
        "createdAt": "2026-07-06T16:18:10+00:00",
        "score": 8,
        "commentCount": 4,
        "previewText": (
            "We are looking at a few different neighborhoods but the school boundary maps on the city site "
            "are a bit confusing. We're planning to attend Northwood High School."
        ),
    },
    {
        "id": "1uonb5y",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "FarNobody5370",
        "title": "Lost cat at Jeffrey Trail",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uonb5y/lost_cat_at_jeffrey_trail/",
        "url": "https://old.reddit.com/r/irvine/comments/1uonb5y/lost_cat_at_jeffrey_trail/",
        "createdAt": "2026-07-06T04:36:28+00:00",
        "score": 54,
        "commentCount": 6,
        "previewText": "Found this guy on the Jeffrey trail leading into Visions.",
    },
    {
        "id": "1uoakdq",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "MichaelUramMFT",
        "title": "The Drone Show/ Fireworks were pretty good in Woodbridge",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uoakdq/the_drone_show_fireworks_were_pretty_good_in/",
        "url": "https://old.reddit.com/r/irvine/comments/1uoakdq/the_drone_show_fireworks_were_pretty_good_in/",
        "createdAt": "2026-07-05T19:06:55+00:00",
        "score": 281,
        "commentCount": 25,
        "previewText": (
            "Woodbridge Village Association had their first drone show and fireworks this year "
            "for their 50th anniversary."
        ),
    },
    {
        "id": "1uo8390",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "Radiant_Lock_7603",
        "title": "Where can you fly a drone?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uo8390/where_can_you_fly_a_drone/",
        "url": "https://old.reddit.com/r/irvine/comments/1uo8390/where_can_you_fly_a_drone/",
        "createdAt": "2026-07-05T17:30:04+00:00",
        "score": 7,
        "commentCount": 5,
        "previewText": (
            "Since moving to OC I thought I could get some really cool shots of the ocean with my drone. "
            "People who have drones where do you fly it?"
        ),
    },
    {
        "id": "1unankr",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "DependentPuzzled2742",
        "title": "July 4th Events in Irvine",
        "permalink": "https://old.reddit.com/r/irvine/comments/1unankr/july_4th_events_in_irvine/",
        "url": "https://old.reddit.com/r/irvine/comments/1unankr/july_4th_events_in_irvine/",
        "createdAt": "2026-07-04T14:35:36+00:00",
        "score": 20,
        "commentCount": 37,
        "previewText": (
            "I noticed Irvine didn't have anything planned. Why can't we get a July 4th event in place?"
        ),
    },
    {
        "id": "1un91mf",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "jms1228",
        "title": "Irvine Civic Center today",
        "permalink": "https://old.reddit.com/r/irvine/comments/1un91mf/irvine_civic_center_today/",
        "url": "https://old.reddit.com/r/irvine/comments/1un91mf/irvine_civic_center_today/",
        "createdAt": "2026-07-04T13:25:33+00:00",
        "score": 179,
        "commentCount": 30,
        "previewText": "It looks amazing!",
    },
    {
        "id": "1umjelf",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "madeyemads",
        "title": "Last seen June 27: HELP MERLIN COME HOME!",
        "permalink": "https://old.reddit.com/r/irvine/comments/1umjelf/last_seen_june_27_help_merlin_come_home/",
        "url": "https://old.reddit.com/r/irvine/comments/1umjelf/last_seen_june_27_help_merlin_come_home/",
        "createdAt": "2026-07-03T16:40:30+00:00",
        "score": 102,
        "commentCount": 16,
        "previewText": (
            "If you have seen or even brought in a black cat since then, that might be Merlin. "
            "500 reward to bring him back!!!"
        ),
    },
    {
        "id": "1um2h4m",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "TravellingFool123",
        "title": "Cookie Monster was in Irvine!!",
        "permalink": "https://old.reddit.com/r/irvine/comments/1um2h4m/cookie_monster_was_in_irvine/",
        "url": "https://old.reddit.com/r/irvine/comments/1um2h4m/cookie_monster_was_in_irvine/",
        "createdAt": "2026-07-03T02:55:53+00:00",
        "score": 52,
        "commentCount": 4,
        "previewText": (
            "This bit was For Sure filmed at the Great Park! Did anyone get an opportunity to see "
            "Cookie Monster when it was filming?"
        ),
    },
    {
        "id": "1um1qku",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "Some_Mine5943",
        "title": "Does USMNT sign autographs after their practices at Great Park?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1um1qku/does_usmnt_sign_autographs_after_their_practices/",
        "url": "https://old.reddit.com/r/irvine/comments/1um1qku/does_usmnt_sign_autographs_after_their_practices/",
        "createdAt": "2026-07-03T02:19:58+00:00",
        "score": 12,
        "commentCount": 11,
        "previewText": (
            "Does USMNT sign autographs after their practices at Great Park? "
            "Did anyone get the chance?"
        ),
    },
    {
        "id": "1ulyxwo",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "pepperonidingleberry",
        "title": "Crème school tuition costs",
        "permalink": "https://old.reddit.com/r/irvine/comments/1ulyxwo/cr%C3%A8me_school_tuition_costs/",
        "url": "https://old.reddit.com/r/irvine/comments/1ulyxwo/cr%C3%A8me_school_tuition_costs/",
        "createdAt": "2026-07-03T00:07:30+00:00",
        "score": 3,
        "commentCount": 10,
        "previewText": (
            "Has anybody received tuition costs for crème? Looking for full or part time for an almost 3 year old."
        ),
    },
    {
        "id": "1uln6t6",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "AccomplishedTitle836",
        "title": "Is Mike Ward park a good place to watch July 4th fireworks?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uln6t6/is_mike_ward_park_a_good_place_to_watch_july_4th/",
        "url": "https://old.reddit.com/r/irvine/comments/1uln6t6/is_mike_ward_park_a_good_place_to_watch_july_4th/",
        "createdAt": "2026-07-02T16:33:14+00:00",
        "score": 9,
        "commentCount": 10,
        "previewText": (
            "Looking for the best place to watch the Woodbridge fireworks with an emphasis on "
            "keeping my sanity when it comes to parking"
        ),
    },
    {
        "id": "1ul39f4",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "DenverToCali",
        "title": "Irvine Co forces to use Parcel Pending for packages and now we are going to get charged if packages aren't picked up in two days (email I got today)",
        "permalink": "https://old.reddit.com/r/irvine/comments/1ul39f4/irvine_co_forces_to_use_parcel_pending_for/",
        "url": "https://old.reddit.com/r/irvine/comments/1ul39f4/irvine_co_forces_to_use_parcel_pending_for/",
        "createdAt": "2026-07-02T00:39:52+00:00",
        "score": 100,
        "commentCount": 105,
        "previewText": (
            "Irvine Company forces residents to use Parcel Pending for packages and now we are going "
            "to get charged if packages aren't picked up in two days."
        ),
    },
    {
        "id": "1ukxhxa",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "Ambitious-Accident14",
        "title": "Happy 4th from the Friends of Katie Wheeler Library!",
        "permalink": "https://old.reddit.com/r/irvine/comments/1ukxhxa/happy_4th_from_the_friends_of_katie_wheeler/",
        "url": "https://old.reddit.com/r/irvine/comments/1ukxhxa/happy_4th_from_the_friends_of_katie_wheeler/",
        "createdAt": "2026-07-01T20:43:50+00:00",
        "score": 25,
        "commentCount": 1,
        "previewText": "Library closed 3rd & 4th, bookstore reopens Monday the 6th 10-4.",
    },
    {
        "id": "1uku663",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "sc0202",
        "title": "New Signal at Harvard and Berkeley Intersection",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uku663/new_signal_at_harvard_and_berkeley_intersection/",
        "url": "https://old.reddit.com/r/irvine/comments/1uku663/new_signal_at_harvard_and_berkeley_intersection/",
        "createdAt": "2026-07-01T18:42:03+00:00",
        "score": 157,
        "commentCount": 16,
        "previewText": (
            "Months ago I submitted a complaint with the city of Irvine for the four way stop sign "
            "intersection at Harvard and Berkeley. Cars speed through it without stopping all the time. "
            "Today I got a voicemail saying that a new signal would be installed there!"
        ),
    },
    {
        "id": "1ukrowc",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "BionicSix",
        "title": '1A "Auditors" in Woodbridge?',
        "permalink": "https://old.reddit.com/r/irvine/comments/1ukrowc/1a_auditors_in_woodbridge/",
        "url": "https://old.reddit.com/r/irvine/comments/1ukrowc/1a_auditors_in_woodbridge/",
        "createdAt": "2026-07-01T17:11:13+00:00",
        "score": 22,
        "commentCount": 25,
        "previewText": (
            'Just drove on E Yale Loop and it looked like some "auditors" were taking pics/videos of cars on the street.'
        ),
    },
    {
        "id": "1ukcke2",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "socalguy31",
        "title": "Mr. Moto Pizza Oak Creek, Irvine",
        "permalink": "https://old.reddit.com/r/irvine/comments/1ukcke2/mr_moto_pizza_oak_creek_irvine/",
        "url": "https://old.reddit.com/r/irvine/comments/1ukcke2/mr_moto_pizza_oak_creek_irvine/",
        "createdAt": "2026-07-01T05:22:39+00:00",
        "score": 20,
        "commentCount": 19,
        "previewText": "It has been almost two years and still no signs of opening. What's going on??",
    },
]

IRVINE_BATCH = {
    "query": "irvine",
    "sort": "new",
    "time": "all",
    "scrapedAt": "2026-07-08T18:17:56.619Z",
    "requestedUrl": "https://old.reddit.com/r/irvine/search/?q=irvine&restrict_sr=on&sort=new&t=all",
    "itemCount": len(IRVINE_ITEMS),
    "items": IRVINE_ITEMS,
}

NEWS_BATCH = {
    "query": "news",
    "sort": "relevance",
    "time": "all",
    "scrapedAt": "2026-07-08T18:02:43.674Z",
    "requestedUrl": "https://old.reddit.com/r/irvine/search/?q=news&restrict_sr=on&t=all",
    "itemCount": len(NEWS_ITEMS),
    "items": NEWS_ITEMS,
}


def _load_existing_items(path: Path) -> list[dict]:
    if not path.is_file() or path.stat().st_size == 0:
        return []
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload.get("items"), list):
        return payload["items"]
    if isinstance(payload.get("scrapes"), list):
        items: list[dict] = []
        for batch in payload["scrapes"]:
            items.extend(batch.get("items") or [])
        return items
    return []


def _dedupe_items(items: list[dict]) -> list[dict]:
    by_id: dict[str, dict] = {}
    for item in items:
        post_id = item.get("id")
        if not post_id:
            continue
        by_id[post_id] = item
    return sorted(
        by_id.values(),
        key=lambda row: row.get("createdAt") or "",
        reverse=True,
    )


def merge_batches(*batches: list[dict], existing: list[dict] | None = None) -> list[dict]:
    combined = list(existing or [])
    for batch in batches:
        combined.extend(batch)
    return _dedupe_items(combined)


def build_payload(items: list[dict], scrapes: list[dict]) -> dict:
    return {
        "blocked": False,
        "listingType": "search",
        "subredditFilter": "irvine",
        "scrapes": scrapes,
        "items": items,
        "itemCount": len(items),
        "queries": [scrape["query"] for scrape in scrapes],
        "scrapedAt": max(scrape["scrapedAt"] for scrape in scrapes),
        "transport": "old-reddit-html",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge Reddit scrape batches into reddit_scrape.json")
    parser.add_argument(
        "--from-json",
        help="Optional JSON file with {items: [...]} or a full scrape export to merge",
    )
    parser.add_argument("--output", default=str(RAW_PATH))
    parser.add_argument("--reprocess", action="store_true", help="Regenerate data/signals/reddit.json after merge")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    existing = _load_existing_items(Path(args.output))

    extra_items: list[dict] = []
    if args.from_json:
        with open(args.from_json, encoding="utf-8") as handle:
            imported = json.load(handle)
        extra_items = imported.get("items") or imported if isinstance(imported, list) else []

    items = merge_batches(NEWS_ITEMS, IRVINE_ITEMS, extra_items, existing=existing)
    scrapes = [NEWS_BATCH, IRVINE_BATCH]
    payload = build_payload(items, scrapes)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    print(f"Merged {len(items)} unique posts -> {output}")
    print(f"  news batch: {len(NEWS_ITEMS)} posts")
    print(f"  irvine batch: {len(IRVINE_ITEMS)} posts")
    if existing:
        print(f"  kept {len(existing)} existing, deduped to {len(items)} total")

    if args.reprocess:
        from scripts.process_reddit_scrape import main as reprocess  # noqa: WPS433

        sys.argv = ["process_reddit_scrape.py"]
        reprocess()


if __name__ == "__main__":
    main()
