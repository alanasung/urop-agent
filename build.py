"""Rank scored postings and emit data.json (for the page) and seen.json (for new-posting detection).

seen.json maps each posting ID to the date it was first seen. A posting is "new" when it was first seen
on the build date, so rebuilding the same day keeps the New tags.
"""
import datetime, json, pathlib, sys

from scored import ROWS

HERE = pathlib.Path(__file__).parent
today = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
prev = json.loads((HERE / "seen.json").read_text()) if (HERE / "seen.json").exists() else {}
if isinstance(prev, list):  # legacy format: plain list of IDs from the 2026-09-23 scan
    prev = {uid: "2026-09-23" for uid in prev}
first_seen = {uid: prev.get(uid, today.isoformat()) for uid in (r[1] for r in ROWS)}
is_first_scan = not prev

# Top MIT labs count as prestige on their own (the student asked to weight these up).
TOP_LABS = ("CSAIL", "Media Lab", "LIDS", "Lincoln", "Koch", "McGovern", "Picower", "Improbable AI")
PRESTIGE_W, FIT_W, REMOTE_BONUS = 15, 4, 2

out = []
for idx, uid, title, dept, pi, pay, hrs, loc, terms, deadline, p, f, note in ROWS:
    closed = False
    if deadline:
        m, d, y = map(int, deadline.split("/"))
        closed = datetime.date(y, m, d) < today
    if any(lab in dept for lab in TOP_LABS):
        p = max(p, 2)
    score = p * PRESTIGE_W + f * FIT_W + (REMOTE_BONUS if loc == "R" else 0)
    out.append(dict(
        id=uid, url=f"https://elx.mit.edu/experience/{uid}", title=title, dept=dept, pi=pi, pay=pay,
        hrs=hrs, remote=loc == "R", iap="IAP" in terms, terms=terms, deadline=deadline, closed=closed,
        prestige=p, fit=f, score=score, note=note,
        new=not is_first_scan and first_seen[uid] == today.isoformat(),
    ))

# IAP-available postings first, then by score.
out.sort(key=lambda r: (r["closed"], not r["iap"], -r["score"], -r["fit"]))
for rank, r in enumerate(out, 1):
    r["rank"] = rank

payload = {"scraped": today.isoformat(), "postings": out}
(HERE / "data.json").write_text(json.dumps(payload, indent=1))
html = (HERE / "template.html").read_text().replace("__DATA__", json.dumps(payload).replace("</", "<\\/"))
(HERE / "urop_shortlist.html").write_text(html)
(HERE / "seen.json").write_text(json.dumps(dict(sorted(first_seen.items())), indent=0))
print(f"{len(out)} postings, {sum(r['closed'] for r in out)} closed, {sum(r['new'] for r in out)} new")
for r in out[:15]:
    print(f"{r['rank']:>3} {'IAP' if r['iap'] else '   '} {r['score']:>3} P{r['prestige']} F{r['fit']} {'R ' if r['remote'] else 'IP'} {r['title'][:70]}")
