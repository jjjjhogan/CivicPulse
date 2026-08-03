# Phase A — Hand Gold Sample (Batch #02)

**Date:** 2026-08-03 (promoted from part A/B)
**Branch:** `feature/phase-a-gold-hand-s4`
**Reviewers:** Jack + coworker (human)
**Signals:** 96 hand-labeled
**Status:** human gold — reusable for Session 5 re-score

> `review_batch_01.md` is AI draft only. This file is the gold sample.
>
> Source worksheets: `batch_01_answers_part_a.txt`, `batch_01_answers_part_b.txt`

## Verdict key

- **correct** — assigned categories fit
- **wrong** — categories do not match content
- **none** — no civic issue / should not be categorized
- **partial** — some categories correct, some wrong or missing

## Summary (human)

| Verdict | Count | % |
|---------|-------|---|
| correct | 41 | 43% |
| wrong | 7 | 7% |
| none | 20 | 21% |
| partial | 28 | 29% |
| **total labeled** | 96 |  |

### By method (human)

| Method | Total | Correct | Wrong | None | Partial |
|--------|-------|---------|-------|------|---------|
| inherited | 41 | 17 | 4 | 0 | 20 |
| keywords | 22 | 11 | 1 | 7 | 3 |
| none | 15 | 2 | 1 | 11 | 1 |
| keywords+model | 12 | 8 | 0 | 0 | 4 |
| model | 5 | 2 | 1 | 2 | 0 |
| legacy | 1 | 1 | 0 | 0 | 0 |

### By source (human)

| Source | Total | Correct | Wrong | None | Partial |
|--------|-------|---------|-------|------|---------|
| tiktok | 60 | 25 | 4 | 7 | 24 |
| reddit | 18 | 13 | 2 | 1 | 2 |
| news | 15 | 2 | 1 | 11 | 1 |
| twitter | 3 | 1 | 0 | 1 | 1 |

## Top failure modes (human)

Approved clusters in [`failure_clusters_draft.md`](failure_clusters_draft.md) (1–7 after human re-bucket).

1. **Inherited categories on non-civic TikTok comments** (15)
2. **Non-civic content that should be uncategorized** (11)
3. **Inherited from parent — video OK, comment weak / partial** (12)
4. **Keyword match in non-civic context** (7)
5. **Wrong category assignment** (5)
6. **Model-only wrong rescues** (2)
7. **Broad keyword false positives** (3)

---

## Raw hand review

Format: `id | source | method | assigned_categories | verdict | notes`

### news (15)

**id=116** · method=`none` · cats=`[]`
- source: <https://www.irvinestandard.com/2026/soak-up-the-serenity/>
> Soak Up the serenity — Tai chi, tall trees and turtles at Heritage Park
`116 | news | none | [] | none | news article of different events in the park.`

**id=118** · method=`none` · cats=`[]`
- source: <https://www.irvinestandard.com/2026/making-the-most-of-a-40-year-run-at-the-barclay/>
> Making the most of a 40-year run at The Barclay — Ginny Hayward probably doesn’t have a copy of the classified ad that ran in a local newspaper in late 1985. Bu…
`118 | news | none | [] | none | article about barclay theater`

**id=120** · method=`none` · cats=`traffic_safety, emergencies`
- source: <https://www.irvinestandard.com/2026/wide-open-opportunities-for-volunteers/>
> Wide-open opportunities for volunteers — A nestling red-tailed hawk, its white head visible above a large nest atop a coast live oak, seems to stand sentry over…
`120 | news | none | traffic_safety, emergencies | wrong | public safeety, emergencies potentially: news article talking about need for more fire watcher volunteers and their importance`

**id=123** · method=`none` · cats=`[]`
- source: <https://www.irvinestandard.com/2026/celebrating-small-business-woodbridge-village-center/>
> Celebrating Small Business: Woodbridge Village Center — Students find their rhythm at Focus Dance Center Leah Lederman began taking lessons at Focus Dance Cente…
`123 | news | none | [] | none | small business article talking about town`

**id=125** · method=`none` · cats=`[]`
- source: <https://www.irvinestandard.com/2026/try-these-5-over-the-top-sandwich-creations/>
> Try these 5 over-the-top sandwich creations — It has been said that life is a sandwich – what happens between slices of the past and future. We say sandwiches a…
`125 | news | none | [] | none | ad for 5 small businesses article`

**id=128** · method=`none` · cats=`public_safety`
- source: <https://www.irvinestandard.com/2026/no-3-city-in-america-to-raise-a-family-2/>
> No. 3 city in America to raise a family — Irvine landed at No. 3 on Wallet­Hub’s national “Best Places to Raise a Family” ranking, driven by its safety record, …
`128 | news | none | public_safety | correct | article talking about a ranking of irvine as no.3 city to raise a family`

**id=129** · method=`none` · cats=`traffic_safety`
- source: <https://www.irvinestandard.com/2026/four-named-national-merit-scholars/>
> Four named National Merit Scholars — Irvine high school students accounted for four of 11 seniors in the county who were awarded prestigious college-sponsored N…
`129 | news | none | traffic_safety | none | article congratulating 4 scholars for their achievement in merit awards`

**id=130** · method=`none` · cats=`[]`
- source: <https://www.irvinestandard.com/2026/10-happenings-in-july/>
> 10 happenings in July — 1. ‘C.S. Lewis on Stage’Experience a multimedia performance capturing the magnetic personality, eloquence and sharp wit of C.S. Lewis. A…
`130 | news | none | [] | correct | july news listings`

**id=131** · method=`none` · cats=`housing`
- source: <https://www.irvinestandard.com/2026/splash-into-summer/>
> Splash into summer — It’s the perfect time to get outside and enjoy the treats of the season – concerts in the park, movies under the stars, hikes on nearby tra…
`131 | news | none | housing | none | summer event ad`

**id=132** · method=`none` · cats=`housing`
- source: <https://www.irvinestandard.com/2026/cutting-edge-connectivity/>
> Cutting-Edge Connectivity — New Irvine Community Pacifica Place Debuts First-of-Its-Kind 3 Gig Wi-Fi 7 Network as High-Speed Internet Becomes a Must-Have Reside…
`132 | news | none | housing | none | talking about updated internet speeds`

**id=133** · method=`none` · cats=`traffic_safety`
- source: <https://www.irvinestandard.com/2026/getting-wild-at-oc-zoo-for-a-day/>
> Getting wild at OC Zoo for a day — About 455 runners of all ages took part in the Run Wild 5K event at the OC Zoo in Irvine Regional Park last month. Proceeds f…
`133 | news | none | traffic_safety | none | article talking about 5k at zoo`

**id=134** · method=`none` · cats=`public_safety, housing`
- source: <https://www.irvinestandard.com/2026/amenities-abound-at-spectrum-terrace/>
> Amenities abound at Spectrum Terrace — Some folks spend work breaks gulping coffee, gobbling doughnuts or playing word games on their phones. Bharat Ananth hits…
`134 | news | none | public_safety, housing | none | ads talking about amenities at apartment complex`

**id=135** · method=`none` · cats=`[]`
- source: <https://www.irvinestandard.com/2026/a-linear-park-journey/>
> A linear park journey — Jeffrey Open Space Trail is a portal to the past and a connection in the present
`135 | news | none | [] | none | new park opening`

**id=136** · method=`none` · cats=`sanitation, traffic_safety, public_safety`
- source: <https://irvineweekly.com/after-an-accident-what-helps-a-personal-injury-claim-most/?utm_source=rss&utm_medium=rss&utm_campaign=after-an-accident-what-helps-a-personal-injury-claim-most>
> After an Accident: What Helps a Personal Injury Claim Most — Details start slipping faster than people expect after an accident. A street name goes fuzzy, the w…
`136 | news | none | sanitation, traffic_safety, public_safety | partial | good news source of what to do if in an accident to keep good details, traffic and public safety potential`

**id=137** · method=`none` · cats=`[]`
- source: <https://irvineweekly.com/aitex-summit-winter-2026-to-spotlight-applied-data-analytics-for-real-world-decisions/?utm_source=rss&utm_medium=rss&utm_campaign=aitex-summit-winter-2026-to-spotlight-applied-data-analytics-for-real-world-decisions>
> AITEX Summit Winter 2026 to Spotlight Applied Data Analytics for Real-World Decisions — Summary: The upcoming AITEX Summit Winter 2026 will bring data analytics…
`137 | news | none | [] | none | ad for tech summet`


### reddit (18)

**id=92** · method=`keywords+model` · cats=`property_crime, public_safety, housing, immigration`
- source: <https://old.reddit.com/r/irvine/comments/1uqoc80/do_irvine_residents_feel_safer_with_flock_cameras/>
> Do Irvine Residents Feel Safer with Flock Cameras everywhere? — Do Irvine Residents Feel Safer with Flock Cameras everywhere? Are the security risks, constant m…
`92 | reddit | keywords+model | property_crime, public_safety, housing, immigration | partial | housing, public_safety is correct, issue with 'invasive' cameras being installed by city`

**id=93** · method=`keywords+model` · cats=`public_safety`
- source: <https://old.reddit.com/r/irvine/comments/1uqilbd/missing_person/>
> Missing Person! — Missing Person! UPDATE - Found and home safe. Thank you, everyone! We need help finding Amy Harchol, a 67-year-old woman. She walked away from…
`93 | reddit | keywords+model | public_safety | correct | missing persons post, who was later found and this is the comment made by irvine pd`

**id=94** · method=`keywords` · cats=`potholes`
- source: <https://old.reddit.com/r/irvine/comments/1uqam9g/our_lovely_new_slurry_seal/>
> Our lovely new slurry seal — Our lovely new slurry seal How is the slurry seal from last week already ruined? Is it melting from the heat? Did it get wet? Did t…
`94 | reddit | keywords | potholes | correct | bad paving job, pothole adjacent news`

**id=95** · method=`keywords` · cats=`noise`
- source: <https://old.reddit.com/r/irvine/comments/1uoakdq/the_drone_show_fireworks_were_pretty_good_in/>
> The Drone Show/ Fireworks were pretty good in Woodbridge — The Drone Show/ Fireworks were pretty good in Woodbridge Woodbridge Village Association had their fir…
`95 | reddit | keywords | noise | correct | firework show is potential noise issue`

**id=96** · method=`keywords` · cats=`noise`
- source: <https://old.reddit.com/r/irvine/comments/1uln6t6/is_mike_ward_park_a_good_place_to_watch_july_4th/>
> Is Mike Ward park a good place to watch July 4th fireworks? — Is Mike Ward park a good place to watch July 4th fireworks? Looking for the best place to watch th…
`96 | reddit | keywords | noise | correct | firework show`

**id=97** · method=`keywords+model` · cats=`traffic_safety`
- source: <https://old.reddit.com/r/irvine/comments/1uku663/new_signal_at_harvard_and_berkeley_intersection/>
> New Signal at Harvard and Berkeley Intersection — New Signal at Harvard and Berkeley Intersection Months ago I submitted a complaint with the city of Irvine for…
`97 | reddit | keywords+model | traffic_safety | correct | the user is talking about the response from the city on adding in a new stoplight, and their excitement for change at this intersection`

**id=98** · method=`legacy` · cats=`public_safety`
- source: <https://old.reddit.com/r/irvine/comments/1ukrowc/1a_auditors_in_woodbridge/>
> 1A "Auditors" in Woodbridge? — 1A "Auditors" in Woodbridge? Just drove on E Yale Loop and it looked like some "auditors" were taking pics/videos of cars on the …
`98 | reddit | legacy | public_safety | correct | potential protest or group of individuals being abrasive`

**id=99** · method=`keywords+model` · cats=`violent_crime, public_safety`
- source: <https://old.reddit.com/r/irvine/comments/1tltzaq/aggressive_coyote_in_turtle_rock_south_irvine/>
> Aggressive coyote in Turtle Rock, south Irvine, killed pet >:( — Aggressive coyote in Turtle Rock, south Irvine, killed pet >:( My parents live in the Turtle Ro…
`99 | reddit | keywords+model | violent_crime, public_safety | partial | public safety, coyote on loose killing pets`

**id=100** · method=`keywords+model` · cats=`housing`
- source: <https://old.reddit.com/r/irvine/comments/1sqr1zd/a_love_letter_to_capitalism_irvine_california/>
> A love letter to capitalism [Irvine, California, 4/19/2026] — A love letter to capitalism [Irvine, California, 4/19/2026] Average rent prices have risen from ab…
`100 | reddit | keywords+model | housing | correct | complaints about rising costs in inflation, housing`

**id=101** · method=`keywords+model` · cats=`public_safety`
- source: <https://old.reddit.com/r/irvine/comments/1sbsc8p/1st_amendment_frauditors_at_woodbury_shopping/>
> “1st Amendment” frauditors at Woodbury shopping center today. — “1st Amendment” frauditors at Woodbury shopping center today. When we drove by they were in fron…
`101 | reddit | keywords+model | public_safety | correct | first admendment protestors arguing with police and causing issues`

**id=102** · method=`keywords` · cats=`violent_crime, public_safety`
- source: <https://old.reddit.com/r/irvine/comments/1r2gjjb/great_park_standoff/>
> Great Park standoff — Great Park standoff https://www.cbsnews.com/losangeles/news/man-irvine-family-hostage-captive-police-standoff/
`102 | reddit | keywords | violent_crime, public_safety | correct | police response to man holding family hostage`

**id=103** · method=`keywords` · cats=`public_safety`
- source: <https://old.reddit.com/r/irvine/comments/1m8qitb/ice_and_ipdirvine_company/>
> ICE and IPD/Irvine Company — ICE and IPD/Irvine Company I've been doing some reading after seeing ICE at spectrum, and it seems like the camera system used by I…
`103 | reddit | keywords | public_safety | wrong | immigration and public safety categories are correct`

**id=104** · method=`keywords+model` · cats=`violent_crime, public_safety`
- source: <https://old.reddit.com/r/irvine/comments/1lglj78/two_people_arrested_after_the_death_of_ten_dogs/>
> Two People Arrested After the Death of Ten Dogs — Two People Arrested After the Death of Ten Dogs On Thursday, Detectives arrested an animal trainer and his gir…
`104 | reddit | keywords+model | violent_crime, public_safety | correct | dog trainers arrested for killing over 10 dogs`

**id=105** · method=`model` · cats=`immigration`
- source: <https://old.reddit.com/r/irvine/comments/1km4u9e/altair_raid_videos/>
> Altair Raid (Videos) — Altair Raid (Videos) FYI - Videos provided by neighbors witnessing the Altair raid (not my content). Still haven't seen any news articles…
`105 | reddit | model | immigration | wrong | public safety, video of police raid`

**id=106** · method=`keywords` · cats=`housing`
- source: <https://old.reddit.com/r/irvine/comments/1kb93jz/wow_happy_tory_for_an_irvine_humble_hero_saw_a/>
> Wow! Happy $tory for an Irvine humble hero. Saw a post on social media, started watching the CBS news video and knew I recognized him! #B... — Wow! Happy $tory …
`106 | reddit | keywords | housing | none | story about homeless man getting donation, not civic signal`

**id=107** · method=`keywords+model` · cats=`traffic_safety`
- source: <https://old.reddit.com/r/irvine/comments/1f1jvtt/irvine_two_motorcyclists_die_in_freeway_crash/>
> Irvine: Two Motorcyclists Die In Freeway Crash (credit: Miles Madison @CountyNewsTV) — Irvine: Two Motorcyclists Die In Freeway Crash (credit: Miles Madison @Co…
`107 | reddit | keywords+model | traffic_safety | correct | traffic collision that caused death`

**id=108** · method=`keywords` · cats=`violent_crime, public_safety`
- source: <https://old.reddit.com/r/irvine/comments/mo5i01/news_irvine_man_tried_to_avenge_crimes_against/>
> [News] Irvine man tried to avenge crimes against Asians by kidnapping and trying to sexually assault a woman
`108 | reddit | keywords | violent_crime, public_safety | correct | violent man arrested for crime`

**id=109** · method=`model` · cats=`public_safety`
- source: <https://old.reddit.com/r/irvine/comments/1c1ut1k/does_anyone_know_these_1st_amendment_auditors/>
> Does anyone know these 1st amendment auditors? — Does anyone know these 1st amendment auditors? I constantly see posts on the Orange County and Irvine subreddit…
`109 | reddit | model | public_safety | correct | 1st amendment auditors filming onpassers and causing issues`


### tiktok (60)

**id=1** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> That’s the most excitement Irvine pd has ever gotten in their career
`1 | tiktok | inherited | public_safety | partial | generic comment about police excitement, video shows traffic issue`

**id=2** · method=`keywords` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> Don’t mess with Irvine cops, they are bored
`2 | tiktok | keywords | public_safety | partial | "cops" keyword, comment is about Irvine police`

**id=3** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> its on the 5 freeway. is it really Irvine? 😁
`3 | tiktok | inherited | public_safety | partial | video is traffic safety`

**id=4** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> That's Tustin 😂😂😂
`4 | tiktok | inherited | public_safety | partial | traffic issue`

**id=5** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> Irvine has been on the news too much lately. Oh how things have changed.
`5 | tiktok | inherited | public_safety | partial | "been on the news too much" — shows issues`

**id=6** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> Did she have to make that statement? God forbid it happen in Irvine
`6 | tiktok | inherited | public_safety | partial | reaction comment, no civic content`

**id=7** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> NEVER woulda happened in a Ford Ranger 💪
`7 | tiktok | inherited | public_safety | partial | "Ford Ranger" joke, zero civic content`

**id=8** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> The man can’t be from Irvine. I see a truck and not a Tesla.
`8 | tiktok | inherited | public_safety | partial | car/Tesla joke`

**id=9** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> I saw this going home . On irvine and Sand Canyon.
`9 | tiktok | inherited | public_safety | partial | "I saw this going home" — no civic issue`

**id=10** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> Kidnap at Bake parkway and Irvine Blvd? That's scary What's the suspect's history?
`10 | tiktok | inherited | public_safety | correct | "Kidnap at Bake parkway" — real public safety concern`

**id=11** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> Did the OC blame this on LA too!!😂😂
`11 | tiktok | inherited | public_safety | partial | "blame this on LA" — joke`

**id=12** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> *** Tustin 😆
`12 | tiktok | inherited | public_safety | partial | "Tustin" — one word correction`

**id=13** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> 👏👏👏IPD👏👏👏
`13 | tiktok | inherited | public_safety | partial | emoji reaction only`

**id=14** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> So it wasn’t successful lol
`14 | tiktok | inherited | public_safety | partial | "wasn't successful" — vague`

**id=15** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> Thats where i work jeesh
`15 | tiktok | inherited | public_safety | partial | "Thats where i work" — no civic content`

**id=16** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> At least they got him fast
`16 | tiktok | inherited | public_safety | partial | "at least they got him fast" — vague reaction`

**id=17** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> So is she OK??
`17 | tiktok | inherited | public_safety | partial | "is she OK??" — concern but no civic content`

**id=18** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> GAAASSSSPPP. I was just there!
`18 | tiktok | inherited | public_safety | partial | reaction exclamation`

**id=19** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@ktlanews/video/7662503385417010446>
> I had a front row view when he got caught!
`19 | tiktok | inherited | public_safety | partial | "front row view when he got caught" — vague`

**id=20** · method=`keywords` · cats=`housing`
- source: <https://www.tiktok.com/@1kjaylive/video/7655861903234747679>
> Only thing scary about Irvine is the home prices and monthly rent! 😭 💴 💴 💴 💴
`20 | tiktok | keywords | housing | none | "home prices and monthly rent" — housing concern`

**id=21** · method=`keywords` · cats=`housing`
- source: <https://www.tiktok.com/@1kjaylive/video/7655861903234747679>
> The rent is the scariest thing in Irvine!
`21 | tiktok | keywords | housing | none | "rent is the scariest thing" — housing complaint`

**id=22** · method=`keywords` · cats=`housing`
- source: <https://www.tiktok.com/@globalgags7/video/7654610369373080854>
> Irvine if Irvine Company Apartments didnt exist
`22 | tiktok | keywords | housing | none | "Irvine Company Apartments" — housing topic`

**id=23** · method=`keywords` · cats=`sanitation`
- source: <https://www.tiktok.com/@kimiaskravings/video/7659407282488315150>
> I’m in Orange County and I just wasted my time watching this useless TikTok. 😏
`23 | tiktok | keywords | sanitation | none | "wasted my time" — not sanitation`

**id=24** · method=`keywords` · cats=`housing`
- source: <https://www.tiktok.com/@kimiaskravings/video/7659407282488315150>
> Um none of these are true except the mortgage lol
`24 | tiktok | keywords | housing | none | "mortgage" appears casually, not a housing issue`

**id=25** · method=`keywords` · cats=`housing`
- source: <https://www.tiktok.com/@miffy_lover6186/video/7647254312330005790>
> hi kaitlyn! I believe you didn’t mean any harm by this video. As a fellow Asian person from Irvine, I totally get the privilege being rai... — hi kaitlyn! I bel…
`25 | tiktok | keywords | housing | none | about Asian identity/privilege, not housing`

**id=26** · method=`keywords` · cats=`emergencies`
- source: <https://www.tiktok.com/@theslickestsu/video/7662468657640951071>
> 😳😳😳that flooding is crazy! Glad it’s not like that all the time
`26 | tiktok | keywords | emergencies | correct | "flooding is crazy" — emergency topic`

**id=27** · method=`keywords` · cats=`emergencies`
- source: <https://www.tiktok.com/@theslickestsu/video/7662468657640951071>
> [Sticker] Oh no, the flooding
`27 | tiktok | keywords | emergencies | correct | "the flooding" — emergency topic`

**id=28** · method=`keywords` · cats=`emergencies`
- source: <https://www.tiktok.com/@theslickestsu/video/7662468657640951071>
> Love the beach wow about the flooding
`28 | tiktok | keywords | emergencies | correct | "about the flooding" — emergency topic`

**id=29** · method=`keywords` · cats=`emergencies`
- source: <https://www.tiktok.com/@vikkzavalaa/video/7662453144110009614>
> No flooding at all I live in Newport Beach 😂
`29 | tiktok | keywords | emergencies | correct | "flooding" mentioned (though denying it) — borderline correct`

**id=30** · method=`keywords+model` · cats=`violent_crime, emergencies`
- source: <https://www.tiktok.com/@vikkzavalaa/video/7662453144110009614>
> It was flooded by the lido bottle last night the 13th
`30 | tiktok | keywords+model | violent_crime, emergencies | partial | "flooded" correct for emergencies, violent_crime is wrong`

**id=32** · method=`model` · cats=`violent_crime`
- source: <https://www.tiktok.com/@skylarensign_/video/7659574575864286494>
> I was there and I live in Newport Beach. It was a lot of locals there. Don’t mean they was destroying things, but it was a lot of locals ... — I was there and I…
`32 | tiktok | model | violent_crime | correct | "destroying things" and yes violence`

**id=33** · method=`keywords` · cats=`public_safety`
- source: <https://www.tiktok.com/@skylarensign_/video/7659574575864286494>
> At least you had police
`33 | tiktok | keywords | public_safety | correct | "police" — correct`

**id=34** · method=`keywords+model` · cats=`sanitation`
- source: <https://www.tiktok.com/@skylarensign_/video/7659574575864286494>
> Its ruins it for the lovely tourists who truly come to have a nice time too. The trash left behind and the complete disregard for others ... — Its ruins it for …
`34 | tiktok | keywords+model | sanitation | correct | "trash left behind" — sanitation issue`

**id=36** · method=`inherited` · cats=`noise`
- source: <https://www.tiktok.com/@abc7la/video/7660348129555844366>
> Social media ruined us
`36 | tiktok | inherited | noise | wrong | video is about public safety and violence in newport`

**id=37** · method=`inherited` · cats=`noise`
- source: <https://www.tiktok.com/@abc7la/video/7660348129555844366>
> Orange County is the Florida of California
`37 | tiktok | inherited | noise | wrong | video on public safety and violence in newport`

**id=39** · method=`inherited` · cats=`noise`
- source: <https://www.tiktok.com/@abc7la/video/7660348129555844366>
> I wish I could have two homes
`39 | tiktok | inherited | noise | wrong | video on firework saftey at newport`

**id=40** · method=`inherited` · cats=`noise`
- source: <https://www.tiktok.com/@abc7la/video/7660348129555844366>
> well well well
`40 | tiktok | inherited | noise | partial | video on public safety in newport`

**id=42** · method=`keywords` · cats=`noise`
- source: <https://www.tiktok.com/@abc7la/video/7660348129555844366>
> Ban fireworks!!!!!!!
`42 | tiktok | keywords | noise | partial | noise complaints and public safety`

**id=47** · method=`inherited` · cats=`noise`
- source: <https://www.tiktok.com/@abc7la/video/7660348129555844366>
> Arizona?!
`47 | tiktok | inherited | noise | partial | video on public safety`

**id=50** · method=`inherited` · cats=`noise`
- source: <https://www.tiktok.com/@abc7la/video/7660348129555844366>
> I’m tired
`50 | tiktok | inherited | noise | partial | video on public safety`

**id=53** · method=`inherited` · cats=`noise`
- source: <https://www.tiktok.com/@abc7la/video/7660348129555844366>
> it took four hours to get off the peninsula 😭
`53 | tiktok | inherited | noise | wrong | vdeo on public safety`

**id=55** · method=`model` · cats=`noise`
- source: <https://www.tiktok.com/@emma.erdman/video/7660299880019152158>
> Joey is open until midnight weekdays and 1 am on weekends. Decent food but definitely better than fast food. Gelsons is open until 11 if ... — Joey is open unti…
`55 | tiktok | model | noise | none | useless video`

**id=73** · method=`keywords` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> The Irvine teenager whose science experiment started a federal investigation and a hazardous materials response a few months ago is once ... — The Irvine teenag…
`73 | tiktok | keywords | public_safety | correct | metal rods in sand = safety issue`

**id=74** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> [Sticker] Sheldon????
`74 | tiktok | inherited | public_safety | correct | Fourth of July chaos, arrests`

**id=76** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> Damn it Shelly!
`76 | tiktok | inherited | public_safety | correct | video is public safety issue`

**id=77** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> Ouu shii👀
`77 | tiktok | inherited | public_safety | correct | public safety issue`

**id=78** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> land of the free
`78 | tiktok | inherited | public_safety | correct | video is public safety`

**id=79** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> but when it's a data center nobody can do a thing
`79 | tiktok | inherited | public_safety | correct | issues is public safety`

**id=80** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> Someone hire that young genius, already!
`80 | tiktok | inherited | public_safety | correct | comment not reliable but video is from news`

**id=81** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> wtf if he concocting today!?
`81 | tiktok | inherited | public_safety | correct | joking comment, good video`

**id=82** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> Right! He didn’t do anything wrong except live
`82 | tiktok | inherited | public_safety | correct | comment disagreeing with arrest, important video`

**id=83** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> give the kid a lab
`83 | tiktok | inherited | public_safety | correct | joking comment, satirical insight on news`

**id=84** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> Government doesn’t want smart people
`84 | tiktok | inherited | public_safety | correct | comment not interesting, inherited important video`

**id=85** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> so my guess is hes figured out something and the government wants it for themselves to profit off of
`85 | tiktok | inherited | public_safety | correct | conspiracy adjacent comment, video important and inherited`

**id=86** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> Look up Die Hard movie.
`86 | tiktok | inherited | public_safety | correct | comment has no substance but video is important`

**id=87** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> So elaborate on the again part?? 🤣 Neighbors must not like the science experiments 😏
`87 | tiktok | inherited | public_safety | correct | joking comment, points out that this is a repeat of similar story with same kid`

**id=88** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> big emphasis on the AGAIN
`88 | tiktok | inherited | public_safety | correct | point out repeat story`

**id=89** · method=`keywords+model` · cats=`violent_crime, public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> His first house was 2.5 million second house was 4 million : his new house is 5.5 million : kid / student ; ruins house = insurance - (no... — His first house w…
`89 | tiktok | keywords+model | violent_crime, public_safety | partial | this comment is a conspiracy about insurance fraud, same public_safety signal as other i would maybe add property_crime here due to the comments information`

**id=90** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> And what does those ingredients do when mixed? I mean I have no clue to lazy to look it up
`90 | tiktok | inherited | public_safety | correct | important comment that showcases this is a chemical issue, mixing chemicals`

**id=91** · method=`inherited` · cats=`public_safety`
- source: <https://www.tiktok.com/@nbcla/video/7659982657522027790>
> Dude was solving fuel shortage
`91 | tiktok | inherited | public_safety | correct | satirical comment about fuel prices, another showcase of scientific chemical part of story.`


### twitter (3)

**id=111** · method=`keywords+model` · cats=`public_safety, traffic_safety`
- source: <https://x.com/IrvinePolice/status/2074865633205088553>
> #IRVINEPDPIO- Around 4:45 a.m., the Orange Police Department pursued a vehicle into Irvine. The pursuit ended in the area of E. Yale Loop... — #IRVINEPDPIO- Aro…
`111 | twitter | keywords+model | public_safety, traffic_safety | correct | police pursuit and arrest of 3 individuals`

**id=113** · method=`model` · cats=`housing`
- source: <https://x.com/newstarjennynam/status/2074921595874021854>
> 남가주 - 얼바인 콘도 리스 $4,590/month 📍 89 Strawberry, Irvine, CA 92620 💰 List Price: $4,590/month 🛏️ 3 Bed | 🛁 3 Bath | 📐 1,567 Sq Ft
`113 | twitter | model | housing | none | housing ad`

**id=115** · method=`keywords` · cats=`emergencies, public safety`
- source: <https://x.com/ABC7/status/2074738553070706879>
> Hazmat response in Irvine is tied to same teen, chemicals from earlier case, attorney says
`115 | twitter | keywords | emergencies, public safety | partial | hazmat response to chemical issue in house`


