#!/usr/bin/env python3
"""Phone-friendly answer key for the marker, generated from quiz-config.json.
Usage: python3 answer_key.py ../../quiz-config.json answer-key.html
Quiz #7 published it as a claude.ai artifact for Darya. Edit ACCEPT (marking notes per round/question) and NAMES for the next quiz."""
import json, re, html, sys
cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
def txt(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()
def parts(qt):  # [(label, points)]
    return [(txt(re.sub(r"<span class=\"q-warn\">.*?</span>", "", a)), int(b)) for a, b in re.findall(r"<p>(.*?)<br\s*/?>\s*<span class=\"q-point\">\((\d+) points?\)</span>", qt)]

# Marking notes for the write-in rounds, keyed by (round, question)
ACCEPT = {
 (2,1): "Accept “Marvin Gay”.",
 (2,2): "Both parts are needed for 2 points: “Windows XP” + “shutting down”. Only one of them (e.g. “Windows shutdown” or “Windows XP start-up”) gets 1 point.",
 (2,3): "Movie: any Rocky film is fine. Song: accept “Gonna Fly Now” or “Theme from Rocky”.",
 (2,4): "Artist: “Macklemore” alone is enough.",
 (2,5): "Accept “WoW”. Plain “Warcraft” is your call (1 point suggested).",
 (2,6): "Movie: “Shawshank” is enough. Narrator: “Freeman” alone is OK.",
 (2,7): "Accept “When I’m 64”.",
 (2,8): "Accept “modem”, “dial-up”, “internet connecting”. “Fax” gets 0.",
 (2,9): "Accept “My Baby Just Cares”.",
 (2,10): "The show’s name is all that’s needed.",
 (3,1): "Accept “Buggles” without “The”.",
 (3,3): "Accept “Sinead” without the accent and “Nothing Compares to You”. Prince (who wrote it) gets 0 for the artist.",
 (3,6): "Greek or Greeklish is fine: Δέσποινα Βανδή / Despina Vandi, Γεια / Gia.",
 (3,9): "Clip is from the Mission: Impossible 2 soundtrack. “Mission Impossible” as the title gets 0.",
 (3,10): "Accept “Freedom”, “Freedom 90”. Wham!’s “Freedom” (1984) is a different song, so “Wham!” gets 0 for the artist.",
 (5,0): "All covers: “The” can be left off band and album names.",
 (5,6): "Accept “Fearless (Taylor’s Version)”.",
 (5,8): "Accept “Joshua Tree” without “The”.",
 (5,10): "It’s a 1996 best-of. “The Number of the Beast” is a different album: 0 for the album.",
 (6,0): "One answer per clip, worth 2 points.",
 (6,2): "John Travolta and Jamie Lee Curtis. Title only.",
 (6,5): "The 2013 remake is also called “Carrie”, so the title alone is fine.",
 (6,6): "Greek or Greeklish, close spellings fine (e.g. “To xylo vgike apo ton paradeiso”).",
 (6,8): "“Top Gun: Maverick” is a different film (2022). Your call; 1 point suggested.",
 (6,9): "Accept “Mrs Doubtfire” without the dot.",
}
NAMES = {1: "Multiple choice", 2: "Sounds", 3: "Music videos", 4: "Multiple choice", 5: "Album covers", 6: "Movie clips"}

rounds = {r: [] for r in range(1, 7)}
for s in cfg["slides"]:
    r, n = s.get("round"), s.get("questionNumber")
    if s["type"] == "question-mcq":
        rounds[r].append(dict(n=n, q=txt(s["questionText"]).replace("(1 point)", "").strip(), letter="ABCD"[s["correctOptionIndex"]],
                              ans=txt(s["options"][s["correctOptionIndex"]]), pts=[("", 1)]))
    elif s["type"] in ("question-audio", "video-clip-timer", "picture-timer"):
        m = re.match(r"(.*?)(?:<br\s*/?>\s*<span class=\"answer-note\">(.*)</span>)?$", s["correctAnswerText"], re.S)
        rounds[r].append(dict(n=n, ans=txt(m.group(1)), note=txt(m.group(2)), pts=parts(s["questionText"])))

def esc(x): return html.escape(x.replace(" — ", " / ").replace("—", ", ").replace("–", "-"), quote=False)
body = []
total = 0
for r in range(1, 7):
    items = sorted(rounds[r], key=lambda d: d["n"]); mx = sum(p for it in items for _, p in it["pts"]); total += mx
    body.append(f'<section id="r{r}"><h2>Round {r} <span class="kind">{NAMES[r]}</span><span class="max">{mx} pts</span></h2>')
    if (r, 0) in ACCEPT: body.append(f'<p class="rule">{esc(ACCEPT[(r,0)])}</p>')
    body.append("<ol>")
    for it in items:
        if "letter" in it:
            body.append(f'<li><span class="n">{it["n"]}</span><div class="a"><b>{it["letter"]}</b> {esc(it["ans"])}'
                        f'<div class="q">{esc(it["q"])}</div></div></li>')
        else:
            split = " + ".join(f"{l.replace('Name the ','')} {p}" for l, p in it["pts"])
            extra = f'<div class="ok">{esc(ACCEPT[(r,it["n"])])}</div>' if (r, it["n"]) in ACCEPT else ""
            note = f' <span class="yr">{esc(it["note"])}</span>' if it["note"] else ""
            body.append(f'<li><span class="n">{it["n"]}</span><div class="a"><b>{esc(it["ans"])}</b>{note}'
                        f'<div class="pts">{esc(split)}</div>{extra}</div></li>')
    body.append("</ol></section>")
nav = " ".join(f'<a href="#r{r}">R{r}</a>' for r in range(1, 7))

page = f'''<title>Quiz #7 Answer Key</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,600;1,400&display=swap">
<style>
/* Layout: one narrow column of plain lines, like a printed answer sheet; sticky round jump bar. */
:root {{
  --paper: #fbfbf8; --ink: #1d1f1c; --muted: #6b6f68; --rule: #dcddd6; --mark: #1f6f3f; --bar: #fbfbf8;
  --mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --paper: #161715; --ink: #e9eae4; --muted: #9a9e95; --rule: #2f312d; --mark: #7fd39b; --bar: #161715; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --paper: #161715; --ink: #e9eae4; --muted: #9a9e95; --rule: #2f312d; --mark: #7fd39b; --bar: #161715; color-scheme: dark; }}
body {{ background: var(--paper); color: var(--ink); font: 15px/1.5 var(--mono);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 0 48px; }}
body::before {{ content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--bar); }}
main {{ max-width: 40rem; margin: 0 auto; }}
header {{ padding-block: 20px 4px; }}
h1 {{ font-size: 1.15rem; font-weight: 600; margin: 0; }}
.meta {{ color: var(--muted); margin: 4px 0 0; font-size: .85rem; }}
nav {{ position: sticky; top: env(safe-area-inset-top, 0px); background: var(--bar); display: flex; gap: 6px; flex-wrap: wrap;
  padding-block: 10px; border-bottom: 1px solid var(--rule); z-index: 5; }}
nav a {{ color: var(--ink); text-decoration: none; border: 1px solid var(--rule); padding: 3px 10px; border-radius: 4px; font-size: .9rem; }}
nav a:focus-visible, nav a:hover {{ border-color: var(--ink); outline: none; }}
section {{ padding-top: 18px; scroll-margin-top: 56px; }}
h2 {{ font-size: 1rem; font-weight: 600; margin: 0 0 6px; display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; }}
.kind {{ font-weight: 400; color: var(--muted); }}
.max {{ margin-left: auto; font-weight: 400; color: var(--muted); font-size: .85rem; font-variant-numeric: tabular-nums; }}
.rule {{ margin: 0 0 6px; color: var(--muted); font-size: .85rem; }}
ol {{ list-style: none; margin: 0; padding: 0; }}
li {{ display: grid; grid-template-columns: 2.2ch 1fr; gap: 10px; padding-block: 8px; border-top: 1px dashed var(--rule); }}
.n {{ color: var(--muted); text-align: right; font-variant-numeric: tabular-nums; }}
.a {{ min-width: 0; overflow-wrap: anywhere; }}
.a b {{ color: var(--mark); font-weight: 600; }}
.yr {{ color: var(--muted); font-size: .85rem; }}
.q, .pts {{ color: var(--muted); font-size: .82rem; }}
.ok {{ font-size: .85rem; margin-top: 3px; }}
.ok::before {{ content: "→ "; color: var(--muted); }}
</style>
<main>
<header><h1>Quiz #7 · answer key</h1>
<p class="meta">Nostalgia Quiz Night · 16 Oct 2026 · {total} points max<br>Small spelling slips are fine unless a note says otherwise.</p></header>
<nav aria-label="Rounds">{nav}</nav>
{"".join(body)}
</main>'''
open(out, "w").write(page)
print("rounds:", {r: len(v) for r, v in rounds.items()}, "total", total)
