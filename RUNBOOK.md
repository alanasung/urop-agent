# UROP shortlist agent — runbook

Goal: keep `urop_shortlist.html` (published at https://claude.ai/artifact/XgZ94CmfHqdzckyWTtrUPu)
current with every UROP on MIT ELx, ranked for the student (alanasng@mit.edu).

## Ranking rules (the student's preferences)
- **Prestige first, then fit.** score = prestige×10 + fit×4 + 2 if remote.
- Prestige 3: named external sponsor/partner (NASA/JPL, MIT Lincoln Lab, IBM / MIT-IBM Watson, GE Vernova,
  DARPA / DoD / US-gov STTR, CERN, Brookhaven, ISS, other big-name companies) or a Nobel-laureate PI.
  Prestige 2: marquee lab/PI (well-known CSAIL / Media Lab / EECS PIs, MGH/Harvard Med collab, FutureTech, etc.).
  Prestige 1: everything else. 0: not really a UROP (startup equity, etc.).
- Fit 5: core AI — agents, LLMs, RL, robot learning, **alignment / interpretability / trustworthy AI** (student likes alignment).
  Fit 4: applied ML. Fit 3: hardware, security, systems/HPC, AI policy. Fit 2: adjacent software/engineering.
  Fit 1: off-profile. Fit 0: wet lab / non-technical.
- Remote preferred (+2) but in person is fine.

## Procedure
1. **Chrome (Claude in Chrome extension)** — the student's Chrome is already signed in to Touchstone.
   `tabs_context_mcp {createIfEmpty:true}` → navigate to https://elx.mit.edu/ and wait ~5 s.
   If the page shows Touchstone/Okta login, STOP: never enter credentials. Notify the student to sign in to ELx in Chrome.
2. Saved preference filters auto-apply (shows ~11). Clear them via JS:
   `[...document.querySelectorAll('button')].find(b=>/Clear Filters/.test(b.innerText)).click()`, wait 4 s,
   confirm the "N experiences" count is the full set (~240+).
3. Collect links: every `a[href^="/experience/"]` → {url, title}. Drop titles matching `/MISTI|Study Abroad/i`.
4. Compare the UUIDs (last path segment) against `seen.json`. Only NEW UUIDs need scraping.
   Also note UUIDs in `scored.py` that are no longer listed (postings removed) — delete those rows.
5. Scrape new postings with hidden same-origin iframes, **max 3 at a time** (8 froze the tab). Detect readiness with a
   MutationObserver on the iframe document (timers get throttled in background tabs): ready when body innerText
   contains "Department/Program" and "Location" and length > 800. 30 s timeout fallback. Store results on `window`.
   Do NOT read the Cognito tokens in localStorage or call api.mit.edu directly.
6. Tool return values truncate at ~1 KB. To read long text, write it into the page
   (`document.body.innerHTML=''`, append `<article id="__dump" style="white-space:pre-wrap">`) and call `get_page_text`.
   Detail page fields appear as label lines: Type, Terms, Estimated Hours Per Week, PI/Faculty Sponsor/Program Director,
   Department/Program (may include "Application deadline; MM/DD/YYYY"), Compensation, Location; description follows "Overview".
   Read the full description for sponsor mentions (the field label "PI/Faculty Sponsor" is NOT a sponsor).
7. Append one tuple per new posting to `ROWS` in `scored.py` (same format; write a short `note` for anything scoring ≥ 34
   naming the sponsor/why). Remove rows for postings that disappeared.
8. `cd /Users/alanasung/Code/urop-agent && python3 build.py` — rebuilds data.json, urop_shortlist.html, seen.json and
   marks new postings with a "New" chip. It prints the counts and top 15.
9. Republish with the Artifact tool: `file_path` = /Users/alanasung/Code/urop-agent/urop_shortlist.html,
   `url` = https://claude.ai/artifact/XgZ94CmfHqdzckyWTtrUPu (read it first if the tool requires).
10. Close the Chrome tab you opened. Report: number of new postings, any new ones scoring ≥ 34 (title, score, why, link),
    and upcoming UROP office deadlines (Fall 2026: sponsored/credit 10/20, supervisor approval 10/22).
    If nothing new, say so in one line.
