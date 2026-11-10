"""Rank scored postings and emit data.json (for the page) and seen.json (for new-posting detection)."""
import datetime, json, pathlib, sys

from scored import ROWS

HERE = pathlib.Path(__file__).parent
today = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
prev_seen = set(json.loads((HERE / "seen.json").read_text())) if (HERE / "seen.json").exists() else None

out = []
for idx, uid, title, dept, pi, pay, hrs, loc, terms, deadline, p, f, note in ROWS:
    closed = False
    if deadline:
        m, d, y = map(int, deadline.split("/"))
        closed = datetime.date(y, m, d) < today
    score = p * 10 + f * 4 + (2 if loc == "R" else 0)
    out.append(dict(
        id=uid, url=f"https://elx.mit.edu/experience/{uid}", title=title, dept=dept, pi=pi, pay=pay,
        hrs=hrs, remote=loc == "R", terms=terms, deadline=deadline, closed=closed,
        prestige=p, fit=f, score=score, note=note,
        new=prev_seen is not None and uid not in prev_seen,
    ))

out.sort(key=lambda r: (r["closed"], -r["score"], -r["fit"]))
for rank, r in enumerate(out, 1):
    r["rank"] = rank

payload = {"scraped": today.isoformat(), "postings": out}
(HERE / "data.json").write_text(json.dumps(payload, indent=1))
html = (HERE / "template.html").read_text().replace("__DATA__", json.dumps(payload).replace("</", "<\\/"))
(HERE / "urop_shortlist.html").write_text(html)
(HERE / "seen.json").write_text(json.dumps(sorted(r["id"] for r in out)))
print(f"{len(out)} postings, {sum(r['closed'] for r in out)} closed, {sum(r['new'] for r in out)} new")
for r in out[:15]:
    print(f"{r['rank']:>3} {r['score']:>3} P{r['prestige']} F{r['fit']} {'R ' if r['remote'] else 'IP'} {r['title'][:70]}")
