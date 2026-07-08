"""One-time seed: write r/irvine news search scrape from manual export."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "raw" / "reddit_scrape.json"

ITEMS = [
    {
        "id": "1uqb87z",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "Salty-Employment6229",
        "title": "Altair in the news again?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1uqb87z/altair_in_the_news_again/",
        "url": "https://old.reddit.com/r/irvine/comments/1uqb87z/altair_in_the_news_again/",
        "createdAt": "2026-07-07T23:07:36+00:00",
        "score": 45,
        "commentCount": 24,
        "previewText": "Three helicopters hovering in place over the community",
    },
    {
        "id": "1pb7sba",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "ShirtFew146",
        "title": "What's the latest news about the soil contamination in the great park neighborhoods?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1pb7sba/whats_the_latest_news_about_the_soil/",
        "url": "https://old.reddit.com/r/irvine/comments/1pb7sba/whats_the_latest_news_about_the_soil/",
        "createdAt": "2025-12-01T08:46:15+00:00",
        "score": 30,
        "commentCount": 22,
        "previewText": (
            "Hi all, I've been looking into the new toll brothers homes in great park but through "
            "my research of the area I came across the former military base and concerns about "
            "soil contamination and subsequent health risks. What's the latest news about the clean "
            "up? Do residents in Irvine feel comfortable about its progress?"
        ),
    },
    {
        "id": "1nflmpr",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "trifelin",
        "title": "Where do you find real time news updates?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1nflmpr/where_do_you_find_real_time_news_updates/",
        "url": "https://old.reddit.com/r/irvine/comments/1nflmpr/where_do_you_find_real_time_news_updates/",
        "createdAt": "2025-09-13T02:10:08+00:00",
        "score": 19,
        "commentCount": 15,
        "previewText": (
            "3 helicopters just flew over my neighborhood and I heard sirens but I just realized "
            "I have no idea where to find local breaking news to see what is happening. Got any links?"
        ),
    },
    {
        "id": "qpa9jy",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "charmed2",
        "title": "Sad news in Irvine",
        "permalink": "https://old.reddit.com/r/irvine/comments/qpa9jy/sad_news_in_irvine/",
        "url": "https://old.reddit.com/r/irvine/comments/qpa9jy/sad_news_in_irvine/",
        "createdAt": "2021-11-08T09:45:43+00:00",
        "score": 65,
        "commentCount": 57,
        "previewText": (
            "Sam Woo's Seafood and BBQ restaurant on Culver is closing! Thanks to the Irvine Company, "
            "as usual. And Mr. Zwart, Northwood High School crossing guard, passed away. He had a fall "
            "while crossing on Yale and Portola."
        ),
    },
    {
        "id": "1kiy5mm",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "UnlikelyLeague8589",
        "title": "Where did the coyote attack happen that is in the news?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1kiy5mm/where_did_the_coyote_attack_happen_that_is_in_the/",
        "url": "https://old.reddit.com/r/irvine/comments/1kiy5mm/where_did_the_coyote_attack_happen_that_is_in_the/",
        "createdAt": "2025-05-10T00:57:41+00:00",
        "score": 12,
        "commentCount": 6,
        "previewText": "https://abc7.com/post/orange-county-coyote-attack-irvine-neighbors-spring-action-rescue-dog/16360484/",
    },
    {
        "id": "1kb93jz",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "deadpanhandling",
        "title": "Wow! Happy $tory for an Irvine humble hero. Saw a post on social media, started watching the CBS news video and knew I recognized him! #BeKind + #payitforward, indeed.",
        "permalink": "https://old.reddit.com/r/irvine/comments/1kb93jz/wow_happy_tory_for_an_irvine_humble_hero_saw_a/",
        "url": "https://old.reddit.com/r/irvine/comments/1kb93jz/wow_happy_tory_for_an_irvine_humble_hero_saw_a/",
        "createdAt": "2025-04-30T05:39:26+00:00",
        "score": 16,
        "commentCount": 4,
        "previewText": "https://www.cbsnews.com/amp/losangeles/news/homeless-man-in-irvine-gifted-nearly-100k-after-donating-his-last-dollar/",
    },
    {
        "id": "1f1jvtt",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "ApexGyrl",
        "title": "Irvine: Two Motorcyclists Die In Freeway Crash (credit: Miles Madison @CountyNewsTV)",
        "permalink": "https://old.reddit.com/r/irvine/comments/1f1jvtt/irvine_two_motorcyclists_die_in_freeway_crash/",
        "url": "https://old.reddit.com/r/irvine/comments/1f1jvtt/irvine_two_motorcyclists_die_in_freeway_crash/",
        "createdAt": "2024-08-26T09:22:01+00:00",
        "score": 19,
        "commentCount": 13,
        "previewText": (
            "Two motorcyclists died in a freeway crash following reports of reckless riding involving "
            "a group of over 50 riders, early Sunday morning on the northbound I-5 Freeway just "
            "south of Culver Drive."
        ),
    },
    {
        "id": "1sqr1zd",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "NicolasCageFan492",
        "title": "A love letter to capitalism [Irvine, California, 4/19/2026]",
        "permalink": "https://old.reddit.com/r/irvine/comments/1sqr1zd/a_love_letter_to_capitalism_irvine_california/",
        "url": "https://old.reddit.com/r/irvine/comments/1sqr1zd/a_love_letter_to_capitalism_irvine_california/",
        "createdAt": "2026-04-20T14:30:55+00:00",
        "score": 371,
        "commentCount": 87,
        "previewText": (
            "Average rent prices have risen from about $300 per month 40 years ago to over $2,000 per "
            "month today. It's incredible how dozens of unhoused people are mocked or blamed for "
            "their difficulties. Thank you, Capitalism, for normalizing victim-shaming."
        ),
    },
    {
        "id": "1gklc75",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "SadSongStreet",
        "title": "News helicopters over UCI",
        "permalink": "https://old.reddit.com/r/irvine/comments/1gklc75/news_helicopters_over_uci/",
        "url": "https://old.reddit.com/r/irvine/comments/1gklc75/news_helicopters_over_uci/",
        "createdAt": "2024-11-06T00:03:05+00:00",
        "score": 11,
        "commentCount": 5,
        "previewText": "Anybody know what's up?",
    },
    {
        "id": "1c7ypcb",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "flatirez",
        "title": "Irvine on CBS News 👀",
        "permalink": "https://old.reddit.com/r/irvine/comments/1c7ypcb/irvine_on_cbs_news/",
        "url": "https://old.reddit.com/r/irvine/comments/1c7ypcb/irvine_on_cbs_news/",
        "createdAt": "2024-04-19T14:47:05+00:00",
        "score": 40,
        "commentCount": 6,
        "previewText": "KCAL9 did an entire segment on the iConnect bus",
    },
    {
        "id": "1fhk2vn",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "rickiethedoog",
        "title": "2024 Mayor Election Candidates Analysis, via Vine City News",
        "permalink": "https://old.reddit.com/r/irvine/comments/1fhk2vn/2024_mayor_election_candidates_analysis_via_vine/",
        "url": "https://old.reddit.com/r/irvine/comments/1fhk2vn/2024_mayor_election_candidates_analysis_via_vine/",
        "createdAt": "2024-09-15T18:54:01+00:00",
        "score": 19,
        "commentCount": 2,
        "previewText": (
            "Seeing how biased many news publications are towards the Election Day, ie. Irvine Community "
            "News & Views, I wanted to share a source that is more on the facts."
        ),
    },
    {
        "id": "ynymrv",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "Shawnj2",
        "title": "Good news- all of the above candidates have their head screwed on in the right direction",
        "permalink": "https://old.reddit.com/r/irvine/comments/ynymrv/good_news_all_of_the_above_candidates_have_their/",
        "url": "https://old.reddit.com/r/irvine/comments/ynymrv/good_news_all_of_the_above_candidates_have_their/",
        "createdAt": "2022-11-06T18:41:30+00:00",
        "score": 64,
        "commentCount": 16,
        "previewText": None,
    },
    {
        "id": "xjig1j",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "solarbeat",
        "title": "Any news on Google and AT&T Fiber?",
        "permalink": "https://old.reddit.com/r/irvine/comments/xjig1j/any_news_on_google_and_att_fiber/",
        "url": "https://old.reddit.com/r/irvine/comments/xjig1j/any_news_on_google_and_att_fiber/",
        "createdAt": "2022-09-20T19:42:50+00:00",
        "score": 10,
        "commentCount": 23,
        "previewText": (
            "Has anyone heard any updates on whether either Google or AT&T have plans to expand their "
            "fiber services in Irvine? It'd be so nice to get out from under Cox."
        ),
    },
    {
        "id": "1km4u9e",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "CaliKoukla",
        "title": "Altair Raid (Videos)",
        "permalink": "https://old.reddit.com/r/irvine/comments/1km4u9e/altair_raid_videos/",
        "url": "https://old.reddit.com/r/irvine/comments/1km4u9e/altair_raid_videos/",
        "createdAt": "2025-05-14T02:54:46+00:00",
        "score": 398,
        "commentCount": 122,
        "previewText": (
            "FYI - Videos provided by neighbors witnessing the Altair raid (not my content). "
            "Still haven't seen any news articles posted."
        ),
    },
    {
        "id": "mo5i01",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "ST012Mi",
        "title": "[News] Irvine man tried to avenge crimes against Asians by kidnapping and trying to sexually assault a woman",
        "permalink": "https://old.reddit.com/r/irvine/comments/mo5i01/news_irvine_man_tried_to_avenge_crimes_against/",
        "url": "https://old.reddit.com/r/irvine/comments/mo5i01/news_irvine_man_tried_to_avenge_crimes_against/",
        "createdAt": "2021-04-10T14:15:17+00:00",
        "score": 25,
        "commentCount": 14,
        "previewText": None,
    },
    {
        "id": "14j5wzk",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "audiomuse1",
        "title": "Tesla Rival Rivian Finally Has Good News on Its Electric Vehicles",
        "permalink": "https://old.reddit.com/r/irvine/comments/14j5wzk/tesla_rival_rivian_finally_has_good_news_on_its/",
        "url": "https://old.reddit.com/r/irvine/comments/14j5wzk/tesla_rival_rivian_finally_has_good_news_on_its/",
        "createdAt": "2023-06-26T03:29:14+00:00",
        "score": 11,
        "commentCount": 1,
        "previewText": None,
    },
    {
        "id": "1tltzaq",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "_myst",
        "title": "Aggressive coyote in Turtle Rock, south Irvine, killed pet >:(",
        "permalink": "https://old.reddit.com/r/irvine/comments/1tltzaq/aggressive_coyote_in_turtle_rock_south_irvine/",
        "url": "https://old.reddit.com/r/irvine/comments/1tltzaq/aggressive_coyote_in_turtle_rock_south_irvine/",
        "createdAt": "2026-05-23T22:20:23+00:00",
        "score": 106,
        "commentCount": 39,
        "previewText": (
            "My parents live in the Turtle Rock neighborhood in southern Irvine, and sadly one of "
            "their cats was likely killed last night. A coyote punched through a screen door. "
            "We've reported the incident to the Irvine Police department and animal control."
        ),
    },
    {
        "id": "1sbsc8p",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "ThePrefect0fWanganui",
        "title": "“1st Amendment” frauditors at Woodbury shopping center today.",
        "permalink": "https://old.reddit.com/r/irvine/comments/1sbsc8p/1st_amendment_frauditors_at_woodbury_shopping/",
        "url": "https://old.reddit.com/r/irvine/comments/1sbsc8p/1st_amendment_frauditors_at_woodbury_shopping/",
        "createdAt": "2026-04-03T22:47:19+00:00",
        "score": 98,
        "commentCount": 44,
        "previewText": (
            "When we drove by they were in front of Ralph's - a bunch of cops were also there arguing "
            "with them. They're being assholes as per usual, masked and aggressive, filming license "
            "plates, getting in people's faces."
        ),
    },
    {
        "id": "1m8qitb",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "Background-Formal598",
        "title": "ICE and IPD/Irvine Company",
        "permalink": "https://old.reddit.com/r/irvine/comments/1m8qitb/ice_and_ipdirvine_company/",
        "url": "https://old.reddit.com/r/irvine/comments/1m8qitb/ice_and_ipdirvine_company/",
        "createdAt": "2025-07-25T05:06:57+00:00",
        "score": 221,
        "commentCount": 65,
        "previewText": (
            "I've been doing some reading after seeing ICE at spectrum, and it seems like the camera "
            "system used by Irvine police and Irvine Company is known to be accessible by ICE."
        ),
    },
    {
        "id": "1th434n",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "OC_Observer",
        "title": "Mailed 4 times a year. This one weighs in at 120 pages.",
        "permalink": "https://old.reddit.com/r/irvine/comments/1th434n/mailed_4_times_a_year_this_one_weighs_in_at_120/",
        "url": "https://old.reddit.com/r/irvine/comments/1th434n/mailed_4_times_a_year_this_one_weighs_in_at_120/",
        "createdAt": "2026-05-18T22:44:35+00:00",
        "score": 48,
        "commentCount": 29,
        "previewText": (
            "Irvine has a budget shortfall. Let's start by ending this massive printed guide sent to "
            "all Irvine households. Isn't it easier to look up programs online?"
        ),
    },
    {
        "id": "1c1ut1k",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "Sweaty_Analysis5607",
        "title": "Does anyone know these 1st amendment auditors?",
        "permalink": "https://old.reddit.com/r/irvine/comments/1c1ut1k/does_anyone_know_these_1st_amendment_auditors/",
        "url": "https://old.reddit.com/r/irvine/comments/1c1ut1k/does_anyone_know_these_1st_amendment_auditors/",
        "createdAt": "2024-04-12T00:09:08+00:00",
        "score": 60,
        "commentCount": 190,
        "previewText": (
            "I constantly see posts on the Orange County and Irvine subreddits about people with masks "
            "filming others at the Sand Canyon Post office."
        ),
    },
    {
        "id": "1r2gjjb",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "EarTotal3258",
        "title": "Great Park standoff",
        "permalink": "https://old.reddit.com/r/irvine/comments/1r2gjjb/great_park_standoff/",
        "url": "https://old.reddit.com/r/irvine/comments/1r2gjjb/great_park_standoff/",
        "createdAt": "2026-02-12T01:50:16+00:00",
        "score": 84,
        "commentCount": 28,
        "previewText": "https://www.cbsnews.com/losangeles/news/man-irvine-family-hostage-captive-police-standoff/",
    },
    {
        "id": "1lglj78",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "Irvinepd",
        "title": "Two People Arrested After the Death of Ten Dogs",
        "permalink": "https://old.reddit.com/r/irvine/comments/1lglj78/two_people_arrested_after_the_death_of_ten_dogs/",
        "url": "https://old.reddit.com/r/irvine/comments/1lglj78/two_people_arrested_after_the_death_of_ten_dogs/",
        "createdAt": "2025-06-21T02:14:31+00:00",
        "score": 235,
        "commentCount": 33,
        "previewText": (
            "On Thursday, Detectives arrested an animal trainer and his girlfriend after ten dogs in "
            "his care died. The Irvine Police Department was contacted and Detectives arrested "
            "Kwong (Tony) Chun Sit, 53, of Irvine, for animal cruelty and destruction of evidence."
        ),
    },
    {
        "id": "1qnuwi3",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "vluong",
        "title": "Irvine Company Announces Nature Park Plans",
        "permalink": "https://old.reddit.com/r/irvine/comments/1qnuwi3/irvine_company_announces_nature_park_plans/",
        "url": "https://old.reddit.com/r/irvine/comments/1qnuwi3/irvine_company_announces_nature_park_plans/",
        "createdAt": "2026-01-26T22:16:16+00:00",
        "score": 41,
        "commentCount": 31,
        "previewText": (
            "Irvine Company officials announced plans for a new nature park on the Oak Creek Golf Club "
            "property, expected to link with the Jeffrey Open Space Trail."
        ),
    },
    {
        "id": "1ty708u",
        "subreddit": "irvine",
        "subredditPrefixed": "r/irvine",
        "author": "sunsetsillybet",
        "title": "Great Park Ducklings: Final Update, only 1/6 ducklings seen",
        "permalink": "https://old.reddit.com/r/irvine/comments/1ty708u/great_park_ducklings_final_update_only_16/",
        "url": "https://old.reddit.com/r/irvine/comments/1ty708u/great_park_ducklings_final_update_only_16/",
        "createdAt": "2026-06-06T04:12:49+00:00",
        "score": 53,
        "commentCount": 9,
        "previewText": (
            "I only saw 1 duckling the hour I was there today, when there were originally 6. "
            "I saw 1 duckling deceased and floating in the pond. Irvine Animal Services left "
            "me a voicemail saying they were going to address the issue and add sandbags in."
        ),
    },
]

PAYLOAD = {
    "blocked": False,
    "listingType": "search",
    "pageTitle": "irvine: search results - news",
    "requestedUrl": "https://old.reddit.com/r/irvine/search/?q=news&restrict_sr=on&t=all",
    "fetchUrl": "https://old.reddit.com/r/irvine/search/?q=news&restrict_sr=on&t=all",
    "finalUrl": "https://old.reddit.com/r/irvine/search/?q=news&restrict_sr=on&t=all",
    "responseStatus": 200,
    "query": "news",
    "sort": "relevance",
    "time": "all",
    "subredditFilter": "irvine",
    "listingTitle": "search",
    "items": ITEMS,
    "itemCount": len(ITEMS),
    "scrapedAt": "2026-07-08T18:02:43.674Z",
    "transport": "old-reddit-html",
}


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(PAYLOAD, handle, indent=2)
    print(f"Wrote {len(ITEMS)} posts -> {OUTPUT}")


if __name__ == "__main__":
    main()
