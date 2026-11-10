# urop-agent

Ranks MIT UROP postings from ELx (elx.mit.edu): sponsor prestige first, then AI fit, with a small bump for remote postings.

- `RUNBOOK.md`: how to scrape ELx through a signed-in Chrome and refresh the list (the weekly scheduled task follows it)
- `scored.py`: one scored row per posting
- `build.py`: ranks the rows and writes `data.json`, `seen.json` and `urop_shortlist.html` from `template.html`

```bash
python3 build.py
```
