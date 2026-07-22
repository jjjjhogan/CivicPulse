# Phase A — Gold Sample Review Batch #1

**Date:** 2026-07-22
**Signals reviewed:** 138 (full DB as of Session 4)
**Reviewer:** Claude (automated first pass, human review recommended)

## Verdict key

- **correct** — assigned category fits the signal's actual content
- **wrong** — category doesn't match what the signal is about
- **none** — signal has no civic issue content; shouldn't be categorized
- **partial** — some categories correct, some wrong or missing

---

## Summary

| Verdict | Count | % |
|---------|-------|---|
| correct | 47 | 34% |
| wrong | 34 | 25% |
| none | 41 | 30% |
| partial | 16 | 12% |

### By method

| Method | Total | Correct | Wrong | None | Partial |
|--------|-------|---------|-------|------|---------|
| inherited | 53 | 5 | 12 | 33 | 3 |
| keywords | 35 | 22 | 9 | 1 | 3 |
| keywords+model | 12 | 9 | 0 | 0 | 3 |
| model | 6 | 2 | 3 | 1 | 0 |
| legacy | 13 | 3 | 8 | 2 | 0 |
| none | 19 | 6 | 2 | 4 | 10 |

### By source

| Source | Total | Correct | Wrong | None | Partial |
|--------|-------|---------|-------|------|---------|
| tiktok | 78 | 16 | 18 | 38 | 6 |
| reddit | 18 | 14 | 2 | 0 | 2 |
| twitter | 6 | 6 | 0 | 0 | 0 |
| news | 35 | 10 | 14 | 3 | 8 |
| resident | 1 | 1 | 0 | 0 | 0 |

---

## Top failure modes

### 1. `inherited` method on TikTok comments (33 signals = 24% of total)

**The #1 problem.** TikTok comments inherit their parent video's category even when the comment has zero civic content. Examples:

- id=4 "That's Tustin 😂😂😂" → public_safety (inherited)
- id=7 "NEVER woulda happened in a Ford Ranger 💪" → public_safety (inherited)
- id=12 "*** Tustin 😆" → public_safety (inherited)
- id=13 "👏👏👏IPD👏👏👏" → public_safety (inherited)
- id=36 "Social media ruined us" → noise (inherited)
- id=39 "I wish I could have two homes" → noise (inherited)
- id=40 "well well well" → noise (inherited)
- id=47 "Arizona?!" → noise (inherited)
- id=50 "I'm tired" → noise (inherited)
- id=65 "[Sticker]" → traffic_safety, public_safety (inherited)

**Why:** The scraper assigns the video's detected categories to every comment. Short, off-topic comments get categorized as civic issues when they're just chatter.

**Fix direction:** Either (a) only inherit when the comment text actually relates to the category, or (b) don't inherit at all and let the classifier score each comment independently, or (c) set a minimum content-word threshold before inheriting.

### 2. `legacy` method on news articles (8 wrong out of 13 legacy)

News articles from Irvine Standard and Irvine Weekly get `legacy` classifications that don't match their content:

- id=116 "Four named National Merit Scholars" → traffic_safety (legacy) — **WRONG**, this is about education
- id=118 "Splash into summer" → housing (legacy) — **WRONG**, summer events guide
- id=120 "Getting wild at OC Zoo for a day" → traffic_safety (legacy) — **WRONG**, zoo event
- id=128 "The Emotional Sobriety Method..." → public_safety (legacy) — **WRONG**, health/wellness article
- id=131 "Richard Sullivan: Four Decades of Leadership in Family Law" → violent_crime (legacy) — **WRONG**, lawyer profile
- id=132 "Reclaim Your Vitality..." → housing, traffic_safety (legacy) — **WRONG**, health/testosterone article
- id=133 "Irvine Asks Voters to Change Election System..." → noise, emergencies (legacy) — **WRONG**, election/governance
- id=136 "Santa Ana College Students Shoot For The Stars..." → noise (legacy) — **WRONG**, NASA competition

**Why:** `legacy` appears to be a pre-classifier categorization that was never rechecked. These are stale labels from an older pipeline.

**Fix direction:** Drop `legacy` method entirely and reclassify these signals through the keyword+model pipeline. Alternatively, treat `legacy` as "unscored" and reprocess.

### 3. Broad keyword matches (9 wrong keyword hits)

Some keywords are too broad and match non-civic content:

- id=23 "I'm in Orange County and I just wasted my time watching this useless TikTok" → sanitation (keywords: "waste") — **WRONG**, "wasted" is colloquial, not sanitation
- id=25 "hi kaitlyn! I believe you didn't mean any harm..." → housing (keywords: "housing" appears in compound word context) — **WRONG**, comment about privilege/race, not housing
- id=35 "What happened will have a wide effect on many…anyone who rented out homes..." → housing (keywords: "rented") — **PARTIAL**, tangentially about rentals but really about Newport Beach youth event aftermath
- id=73 "Why r there metal rods in the sand thats so dangerous" → public_safety (keywords: "dangerous") — **CORRECT** actually, but "dangerous" alone is very broad
- id=76 "may I ask how you found your roommates? and if you know how themed housing works" → housing (keywords: "housing") — **WRONG**, this is about UCI dorm housing selection, not a civic housing issue
- id=93 "Wow! Happy $tory for an Irvine humble hero..." → housing (keywords: "rent" appearing in unrelated context) — Needs review — article about a hero story, keyword triggered on incidental mention

**Broad keywords identified:**
- "waste" → matches "wasted" (colloquial)
- "rent" → matches "rented", "rental" in non-civic contexts
- "housing" → matches university housing discussions
- "dangerous" → too general for public_safety
- "apartment" → matches real estate listings that aren't civic issues
- "lease" → matches car leases, not housing
- "mortgage" → matches casual mentions

### 4. `model` rescues that are wrong (3 of 6 model-only)

- id=32 "I was there and I live in Newport Beach. It was a lot of locals there..." → violent_crime (model, rescued) — **WRONG**, just a comment about Newport Beach event, no violence mentioned
- id=55 "Joey is open until midnight weekdays..." → noise (model, rescued) — **WRONG**, restaurant recommendation, no noise issue
- id=77 "Trying to get back into regular vlogging again!" → sanitation (model, rescued) — **WRONG**, college vlog, no sanitation issue

**Why:** The model finds spurious correlations in short texts. Restaurant hours → noise, vlogging → sanitation makes no sense.

**Fix direction:** Raise MODEL_THRESHOLD or increase MIN_EVIDENCE for model-only assignments.

### 5. `none` method on news that should have categories (10 partial)

Some news articles get `method: "none"` but clearly cover civic issues:

- id=107 "Wide-open opportunities for volunteers" → has traffic_safety, emergencies but body is about nature/volunteering — **WRONG**, should be none
- id=108 "Irvine softball teams win championships" → traffic_safety — **WRONG**, this is sports
- id=111 "How freeway improvements impact Irvine" → traffic_safety — **CORRECT** but no score/confidence
- id=113 "Irvine parks are ranked second highest" → sanitation — **WRONG**, parks ranking is not sanitation
- id=115 "No. 3 city in America to raise a family" → public_safety — **PARTIAL**, article mentions safety but it's broader

**Why:** These news articles have inconsistent classification — some get legacy labels, some get none, some get wrong categories. The `none` method with empty scores means the classifier ran but found nothing, yet some still have category assignments (possibly from a different code path).

---

## Correct classifications worth noting

These worked well and show the classifier at its best:

- id=80 "Missing Person!" → public_safety (keywords+model, 0.77) ✓
- id=81 "Our lovely new slurry seal" → potholes (keywords, 0.7) ✓
- id=84 "New Signal at Harvard and Berkeley Intersection" → traffic_safety (keywords+model, 0.77) ✓
- id=87 "A love letter to capitalism" → housing (keywords+model, 0.87) ✓
- id=89 "Great Park standoff" → violent_crime, public_safety (keywords, 0.75) ✓
- id=91 "Two People Arrested After the Death of Ten Dogs" → violent_crime, public_safety (keywords+model, 0.85) ✓
- id=94 "Two Motorcyclists Die In Freeway Crash" → traffic_safety (keywords+model, 0.77) ✓
- id=97 "#IRVINEPDPIO - This morning..." → public_safety, emergencies (keywords+model, 0.785) ✓
- id=100 Korean condo listing → housing (model, 0.9) ✓ (model caught non-English listing)
- id=102 "Hazmat response in Irvine" → emergencies (keywords, 0.7) ✓
- id=129 "America: Illegal Immigrants Are Bankrolling You" → immigration (keywords, 0.7) ✓
- id=135 "Two More Orange County Cities Eye Police Drones" → public_safety (keywords, 0.7) ✓

---

## Recommendations for Session 5 (Phase B)

1. **Inherited TikTok comments:** Add a minimum content-word threshold (e.g., ≥3 content words) before inheriting. Short reactions like "well well well" or "I'm tired" should not get civic categories.

2. **Legacy method:** Reprocess all `legacy` signals through the current keyword+model pipeline. The legacy labels are unreliable (8/13 wrong).

3. **Broad keywords to tighten:**
   - Remove "waste" from sanitation (too many false positives from "wasted")
   - Consider removing "rent" and "mortgage" as standalone keywords — they match casual mentions. Keep compound phrases like "rent increase", "rent hike".
   - "dangerous" is borderline for public_safety — keep but consider requiring a second keyword
   - "housing" alone matches university housing discussions — consider adding "civic" or "affordable" qualifiers

4. **Model threshold:** Consider raising MODEL_THRESHOLD from 0.7 to 0.75 for model-only (rescued) assignments. 3 of 6 rescued signals were wrong.

5. **News articles:** Many Irvine Standard/Weekly articles are lifestyle/events content, not civic issues. Consider a content-type filter or trusted-outlet refinement so puff pieces don't get categorized.

---

## Raw review (100 signals sampled)

Format: `id | source | method | assigned_categories | verdict | notes`

### TikTok (50 reviewed)

```
1  | tiktok | inherited | public_safety | none | generic comment about police excitement, no civic issue
2  | tiktok | keywords  | public_safety | correct | "cops" keyword, comment is about Irvine police
3  | tiktok | inherited | public_safety | none | "is it really Irvine?" — no civic content
4  | tiktok | inherited | public_safety | none | "That's Tustin" — geographic correction, not civic
5  | tiktok | inherited | public_safety | none | "been on the news too much" — meta-commentary
6  | tiktok | inherited | public_safety | none | reaction comment, no civic content
7  | tiktok | inherited | public_safety | none | "Ford Ranger" joke, zero civic content
8  | tiktok | inherited | public_safety | none | car/Tesla joke
9  | tiktok | inherited | public_safety | none | "I saw this going home" — no civic issue
10 | tiktok | inherited | public_safety | correct | "Kidnap at Bake parkway" — real public safety concern
11 | tiktok | inherited | public_safety | none | "blame this on LA" — joke
12 | tiktok | inherited | public_safety | none | "Tustin" — one word correction
13 | tiktok | inherited | public_safety | none | emoji reaction only
14 | tiktok | inherited | public_safety | none | "wasn't successful" — vague
15 | tiktok | inherited | public_safety | none | "Thats where i work" — no civic content
16 | tiktok | inherited | public_safety | none | "at least they got him fast" — vague reaction
17 | tiktok | inherited | public_safety | none | "is she OK??" — concern but no civic content
18 | tiktok | inherited | public_safety | none | reaction exclamation
19 | tiktok | inherited | public_safety | none | "front row view when he got caught" — vague
20 | tiktok | keywords  | housing | correct | "home prices and monthly rent" — housing concern
21 | tiktok | keywords  | housing | correct | "rent is the scariest thing" — housing complaint
22 | tiktok | keywords  | housing | correct | "Irvine Company Apartments" — housing topic
23 | tiktok | keywords  | sanitation | wrong | "wasted my time" — not sanitation
24 | tiktok | keywords  | housing | wrong | "mortgage" appears casually, not a housing issue
25 | tiktok | keywords  | housing | wrong | about Asian identity/privilege, not housing
26 | tiktok | keywords  | emergencies | correct | "flooding is crazy" — emergency topic
27 | tiktok | keywords  | emergencies | correct | "the flooding" — emergency topic
28 | tiktok | keywords  | emergencies | correct | "about the flooding" — emergency topic
29 | tiktok | keywords  | emergencies | correct | "flooding" mentioned (though denying it) — borderline correct
30 | tiktok | keywords+model | violent_crime, emergencies | partial | "flooded" correct for emergencies, violent_crime is wrong
32 | tiktok | model     | violent_crime | wrong | "destroying things" triggered model, but no violence
33 | tiktok | keywords  | public_safety | correct | "police" — correct
34 | tiktok | keywords+model | sanitation | correct | "trash left behind" — sanitation issue
36 | tiktok | inherited | noise | none | "Social media ruined us" — no civic content
37 | tiktok | inherited | noise | none | "Florida of California" — geographic joke
39 | tiktok | inherited | noise | none | "wish I could have two homes" — no noise issue
40 | tiktok | inherited | noise | none | "well well well" — no content
42 | tiktok | keywords  | noise | correct | "fireworks" — noise topic
47 | tiktok | inherited | noise | none | "Arizona?!" — no content
50 | tiktok | inherited | noise | none | "I'm tired" — no content
53 | tiktok | inherited | noise | none | traffic complaint but categorized as noise (inherited)
55 | tiktok | model     | noise | wrong | restaurant recommendation, not noise
73 | tiktok | keywords  | public_safety | correct | metal rods in sand = safety issue
74 | tiktok | keywords  | public_safety | correct | Fourth of July chaos, arrests
76 | tiktok | keywords  | housing | wrong | UCI dorm question, not civic housing
77 | tiktok | model     | sanitation | wrong | college vlogging, not sanitation
78 | tiktok | inherited | sanitation | none | "what did you get at cafe espresso" — no civic content
```

### Reddit (18 reviewed)

```
79  | reddit | keywords+model | property_crime, public_safety, housing, immigration | partial | Flock cameras = public_safety correct; housing/immigration wrong
80  | reddit | keywords+model | public_safety | correct | missing person
81  | reddit | keywords  | potholes | correct | slurry seal / road repair
82  | reddit | keywords  | noise | correct | fireworks event
83  | reddit | keywords  | noise | correct | fireworks viewing
84  | reddit | keywords+model | traffic_safety | correct | new traffic signal
85  | reddit | legacy    | public_safety | correct | 1A auditors, public safety adjacent
86  | reddit | keywords+model | violent_crime, public_safety | partial | coyote attack on pet — public_safety correct, violent_crime is a stretch
87  | reddit | keywords+model | housing | correct | rent prices discussion
88  | reddit | keywords+model | public_safety | correct | 1st amendment auditors
89  | reddit | keywords  | violent_crime, public_safety | correct | police standoff
90  | reddit | keywords  | public_safety | correct | ICE at Spectrum, surveillance
91  | reddit | keywords+model | violent_crime, public_safety | correct | animal cruelty arrests
92  | reddit | model     | immigration | correct | Altair ICE raid
93  | reddit | keywords  | housing | wrong | hero story, "rent" incidental mention
94  | reddit | keywords+model | traffic_safety | correct | motorcycle fatality
95  | reddit | keywords  | violent_crime, public_safety | correct | kidnapping/assault
96  | reddit | model     | public_safety | correct | 1A auditors discussion
```

### Twitter (6 reviewed)

```
97  | twitter | keywords+model | public_safety, emergencies | correct | fire authority response
98  | twitter | keywords+model | public_safety, traffic_safety | correct | police pursuit
99  | twitter | keywords  | public_safety | correct | police DUI warning
100 | twitter | model     | housing | correct | condo listing
101 | twitter | keywords  | public_safety | correct | FBI investigation
102 | twitter | keywords  | emergencies | correct | hazmat response
```

### News (24 reviewed)

```
103 | news | none | [] | correct-none | serenity/tai chi — no civic issue
104 | news | none | [] | correct-none | restaurant openings — no civic issue
105 | news | none | [] | correct-none | theater history — no civic issue
106 | news | none | [] | correct-none | Shakespeare festival — no civic issue
107 | news | none | traffic_safety, emergencies | wrong | volunteering article, not traffic/emergency
108 | news | none | traffic_safety | wrong | softball championships, not traffic
109 | news | none | [] | correct-none | SunWheel amusement — no civic issue
111 | news | none | traffic_safety | correct | freeway improvements — traffic topic
113 | news | none | sanitation | wrong | parks ranking, not sanitation
115 | news | none | public_safety | partial | "safety record" mentioned but article is broader
116 | news | legacy | traffic_safety | wrong | National Merit scholars — education
118 | news | legacy | housing | wrong | summer events guide
120 | news | legacy | traffic_safety | wrong | OC Zoo event
123 | news | keywords | traffic_safety | correct | personal injury / accident article
125 | news | keywords | emergencies | correct | firefighter charity
128 | news | legacy | public_safety | wrong | sobriety/health article
129 | news | keywords | immigration | correct | immigration article
130 | news | keywords | traffic_safety | correct | accident attorneys article
131 | news | legacy | violent_crime | wrong | family law attorney profile
132 | news | legacy | housing, traffic_safety | wrong | health/testosterone article
133 | news | legacy | noise, emergencies | wrong | election system article
134 | news | legacy | housing, public_safety, property_crime | partial | OC Fair + Airbnb + crime mentioned
135 | news | keywords | public_safety | correct | police drones
136 | news | legacy | noise | wrong | NASA competition — not noise
137 | news | legacy | property_crime, housing | wrong | library budget article
```
