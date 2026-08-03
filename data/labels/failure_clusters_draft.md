# Failure-mode clusters — APPROVED (human re-bucketed)

**Date:** 2026-08-03  
**From:** 96 human gold rows · 55 wrong/none/partial  
**Status:** human-edited — clusters 1–7 (old 5 and 9 removed; renumbered)

## Moves applied

| id | from | to (pre-renumber) |
|----|------|-------------------|
| 2 | 5 | 3 |
| 30 | 5 | 6 |
| 42 | 5 | 1 |
| 89 | 5 | 6 |
| 99 | 5 | 6 |
| 115 | 5 | 3 |
| 136 | 9 | 8 |

Then dropped empty old 5 and 9; renumbered old 6→5, 7→6, 8→7.

## Tally snapshot

- correct 41 (43%)
- partial 28 (29%)
- none 20 (21%)
- wrong 7 (7%)

---

## 1. Inherited categories on non-civic TikTok comments (15)

Comment text has no civic issue, but cats came from parent video (`method=inherited`). (Includes id 42 per human re-bucket.)

| id | source | method | cats | verdict | note |
|----|--------|--------|------|---------|------|
| 6 | tiktok | inherited | public_safety | partial | reaction comment, no civic content |
| 7 | tiktok | inherited | public_safety | partial | "Ford Ranger" joke, zero civic content |
| 8 | tiktok | inherited | public_safety | partial | car/Tesla joke |
| 9 | tiktok | inherited | public_safety | partial | "I saw this going home" — no civic issue |
| 11 | tiktok | inherited | public_safety | partial | "blame this on LA" — joke |
| 12 | tiktok | inherited | public_safety | partial | "Tustin" — one word correction |
| 13 | tiktok | inherited | public_safety | partial | emoji reaction only |
| 14 | tiktok | inherited | public_safety | partial | "wasn't successful" — vague |
| 15 | tiktok | inherited | public_safety | partial | "Thats where i work" — no civic content |
| 16 | tiktok | inherited | public_safety | partial | "at least they got him fast" — vague reaction |
| 17 | tiktok | inherited | public_safety | partial | "is she OK??" — concern but no civic content |
| 18 | tiktok | inherited | public_safety | partial | reaction exclamation |
| 19 | tiktok | inherited | public_safety | partial | "front row view when he got caught" — vague |
| 42 | tiktok | keywords | noise | partial | noise complaints and public safety |
| 53 | tiktok | inherited | noise | wrong | vdeo on public safety |

## 2. Non-civic content that should be uncategorized (11)

Lifestyle / fluff / chatter; humans marked `none`.

| id | source | method | cats | verdict | note |
|----|--------|--------|------|---------|------|
| 106 | reddit | keywords | housing | none | story about homeless man getting donation, not civic signal |
| 118 | news | none | `[]` | none | article about barclay theater |
| 123 | news | none | `[]` | none | small business article talking about town |
| 125 | news | none | `[]` | none | ad for 5 small businesses article |
| 129 | news | none | traffic_safety | none | article congratulating 4 scholars for their achievement in merit awards |
| 131 | news | none | housing | none | summer event ad |
| 132 | news | none | housing | none | talking about updated internet speeds |
| 133 | news | none | traffic_safety | none | article talking about 5k at zoo |
| 134 | news | none | public_safety, housing | none | ads talking about amenities at apartment complex |
| 135 | news | none | `[]` | none | new park opening |
| 137 | news | none | `[]` | none | ad for tech summet |

## 3. Inherited from parent — video OK, comment weak / partial (12)

Humans often say the video is civic but the comment is chatter; inherited cats still apply to the comment row.

| id | source | method | cats | verdict | note |
|----|--------|--------|------|---------|------|
| 1 | tiktok | inherited | public_safety | partial | generic comment about police excitement, video shows traffic issue |
| 2 | tiktok | keywords | public_safety | partial | "cops" keyword, comment is about Irvine police |
| 3 | tiktok | inherited | public_safety | partial | video is traffic safety |
| 4 | tiktok | inherited | public_safety | partial | traffic issue |
| 5 | tiktok | inherited | public_safety | partial | "been on the news too much" — shows issues |
| 36 | tiktok | inherited | noise | wrong | video is about public safety and violence in newport |
| 37 | tiktok | inherited | noise | wrong | video on public safety and violence in newport |
| 39 | tiktok | inherited | noise | wrong | video on firework saftey at newport |
| 40 | tiktok | inherited | noise | partial | video on public safety in newport |
| 47 | tiktok | inherited | noise | partial | video on public safety |
| 50 | tiktok | inherited | noise | partial | video on public safety |
| 115 | twitter | keywords | emergencies, public safety | partial | hazmat response to chemical issue in house |

## 4. Keyword match in non-civic context (7)

Real keyword string, but topic is not a city civic issue (e.g. dorm housing).

| id | source | method | cats | verdict | note |
|----|--------|--------|------|---------|------|
| 20 | tiktok | keywords | housing | none | "home prices and monthly rent" — housing concern |
| 21 | tiktok | keywords | housing | none | "rent is the scariest thing" — housing complaint |
| 22 | tiktok | keywords | housing | none | "Irvine Company Apartments" — housing topic |
| 25 | tiktok | keywords | housing | none | about Asian identity/privilege, not housing |
| 92 | reddit | keywords+model | property_crime, public_safety, housing, immigration | partial | housing, public_safety is correct, issue with 'invasive' cameras being installed by city |
| 113 | twitter | model | housing | none | housing ad |
| 116 | news | none | `[]` | none | news article of different events in the park. |

## 5. Wrong category assignment (5)

Has civic-ish or other content, but assigned cat(s) do not fit.

| id | source | method | cats | verdict | note |
|----|--------|--------|------|---------|------|
| 30 | tiktok | keywords+model | violent_crime, emergencies | partial | "flooded" correct for emergencies, violent_crime is wrong |
| 89 | tiktok | keywords+model | violent_crime, public_safety | partial | this comment is a conspiracy about insurance fraud, same public_safety signal as other i would maybe add property_crime here due to the comments information |
| 99 | reddit | keywords+model | violent_crime, public_safety | partial | public safety, coyote on loose killing pets |
| 103 | reddit | keywords | public_safety | wrong | immigration and public safety categories are correct |
| 120 | news | none | traffic_safety, emergencies | wrong | public safeety, emergencies potentially: news article talking about need for more fire watcher volunteers and their importance |

## 6. Model-only wrong rescues (2)

`method=model` assigned a category that humans reject.

| id | source | method | cats | verdict | note |
|----|--------|--------|------|---------|------|
| 55 | tiktok | model | noise | none | useless video |
| 105 | reddit | model | immigration | wrong | public safety, video of police raid |

## 7. Broad keyword false positives (3)

Keyword hit on colloquial / incidental words (e.g. waste/wasted, mortgage). (Includes id 136 per human re-bucket.)

| id | source | method | cats | verdict | note |
|----|--------|--------|------|---------|------|
| 23 | tiktok | keywords | sanitation | none | "wasted my time" — not sanitation |
| 24 | tiktok | keywords | housing | none | "mortgage" appears casually, not a housing issue |
| 136 | news | none | sanitation, traffic_safety, public_safety | partial | good news source of what to do if in an accident to keep good details, traffic and public safety potential |
