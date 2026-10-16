#!/usr/bin/env python3
"""Build Quiz #7 quiz-config.json from the #6 config as a template.
Rounds with no data yet render as a clearly-marked placeholder slide.
Usage: python3 build_config.py   (writes ../nostalgia-quiz-night/quiz-config.json)"""
import json, copy, os, re
from rounds import R1, R2, R3, R4, R5, R6, SETTINGS, PRIZES, THEME, CHARITY
try:
    from rounds import HALFTIME
except ImportError:
    HALFTIME = []
try:
    from rounds import FINAL
except ImportError:
    FINAL = []
try:
    from rounds import TIE_WINNERS
except ImportError:
    TIE_WINNERS = {}

HERE = os.path.dirname(os.path.abspath(__file__))
# Works both from the repo (tools/quiz-builder/) and from the old ~/nostalgia/q7-build working dir.
APP = os.path.join(HERE, "..", "..") if os.path.exists(os.path.join(HERE, "..", "..", "app.js")) else os.path.join(HERE, "..", "nostalgia-quiz-night")
tpl = json.load(open(os.path.join(os.path.dirname(__file__), "q6-template.json")))
T = {s["id"]: s for s in tpl["slides"]}

def q(text_parts):
    """[(label, points)] -> questionText in the #6 house style."""
    return "".join(f'<p>{lbl}<br /><span class="q-point">({p} point{"s" if p != 1 else ""})</span></p>' for lbl, p in text_parts)

def ans(main, note=None):
    return main + (f'<br /><span class="answer-note">{note}</span>' if note else "")

def placeholder(r, what):
    return [{"id": f"r{r}-todo", "type": "info", "title": f"⚠ Round {r} — {what} not added yet",
             "subtitle": "Placeholder: this slide must not appear on the night"}]

def round_block(r, qslides, answer_refs):
    out = [copy.deepcopy(T[f"round{r}-intro"])] + qslides
    out += [copy.deepcopy(T[f"r{r}-collection"]), copy.deepcopy(T[f"r{r}-answers-intro"])]
    out += [{"id": f"r{r}-a{i}", "type": "answer", "questionRefId": ref, "title": "Answer"} for i, ref in enumerate(answer_refs, 1)]
    return out

def mcq_round(r, items):
    if not items: return placeholder(r, "multiple-choice questions")
    qs = []
    for i, it in enumerate(items, 1):
        qs.append({"id": f"r{r}-q{i}", "type": "question-mcq", "round": r, "questionNumber": i,
                   "questionText": f'<p>{it["q"]}<br /><span class="q-point">(1 point)</span></p>',
                   "options": it["options"], "correctOptionIndex": it["correct"], "timerSeconds": 30})
    return round_block(r, qs, [f"r{r}-q{i}" for i in range(1, len(items) + 1)])

def audio_round(r, items):
    if not items: return placeholder(r, "sounds")
    qs = [{"id": f"r{r}-q{i}", "type": "question-audio", "round": r, "questionNumber": i,
           "questionText": q(it["parts"]), "audioSrc": f"media/r{r}-q{i}.mp3", "timerSeconds": 30,
           "correctAnswerText": ans(it["answer"], it.get("note"))} for i, it in enumerate(items, 1)]
    return round_block(r, qs, [f"r{r}-q{i}" for i in range(1, len(items) + 1)])

def video_round(r, items, what):
    if not items: return placeholder(r, what)
    qs = []
    for i, it in enumerate(items, 1):
        qt = q(it["parts"])
        qs += [{"id": f"r{r}-q{i}-question", "type": "video-clip", "round": r, "questionNumber": i, "questionText": qt},
               {"id": f"r{r}-q{i}-play", "type": "video-fullscreen", "videoSrc": f"media/r{r}-q{i}.mp4"},
               {"id": f"r{r}-q{i}-timer", "type": "video-clip-timer", "round": r, "questionNumber": i, "questionText": qt,
                "timerSeconds": 30, "correctAnswerText": ans(it["answer"], it.get("note"))}]
    return round_block(r, qs, [f"r{r}-q{i}-timer" for i in range(1, len(items) + 1)])

def picture_round(r, items):
    if not items: return placeholder(r, "pictures")
    qs = []
    for i, it in enumerate(items, 1):
        qt = q(it["parts"])
        qs += [{"id": f"r{r}-q{i}-question", "type": "picture-question", "round": r, "questionNumber": i, "questionText": qt},
               {"id": f"r{r}-q{i}-show", "type": "picture-fullscreen", "image": it.get("src", f"media/r{r}-q{i}.jpg")},
               {"id": f"r{r}-q{i}-timer", "type": "picture-timer", "round": r, "questionNumber": i, "questionText": qt,
                "image": it.get("src", f"media/r{r}-q{i}.jpg"), "timerSeconds": 30, "correctAnswerText": ans(it["answer"], it.get("note"))}]
    return round_block(r, qs, [f"r{r}-q{i}-timer" for i in range(1, len(items) + 1)])

def blank_scores(prefix_ids):
    """Halftime/final team slides: keep layout, wipe #6 names/points."""
    out = []
    for sid in prefix_ids:
        s = copy.deepcopy(T[sid])
        if "htmlContent" in s and ("points" in s["htmlContent"] or "&mdash;" in s["htmlContent"]):
            s["htmlContent"] = "<div style='text-align: center; font-size: 3em; margin-top: 1em; color: #888;'>TBC</div>"
        out.append(s)
    return out

slides = [copy.deepcopy(T["welcome"]), copy.deepcopy(T["welcome-2"])]
# White full-slide panel (covers the green-brick info background): photo on top, message below.
_lines = "".join(f"<p style='margin: 0.3em auto 0; max-width: 92vw; font-size: 2.5rem; line-height: 1.3; color: #333;'>{l}</p>" for l in CHARITY["lines"])
slides.append({"id": "charity-voice-for-autism", "type": "info", "htmlContent":
    "<div style='position: fixed; inset: 0; z-index: 5; background: #ffffff; display: flex; flex-direction: column; "
    "align-items: center; justify-content: center; padding: 1.5vh 2vw; text-align: center;'>"
    f"<img src='{CHARITY['image']}' alt='' style='max-height: 63vh; max-width: 96vw; border-radius: 8px; "
    "box-shadow: 0 6px 24px rgba(0,0,0,0.18);'>"
    f"<h1 style='margin: 0.35em 0 0.05em; font-size: 4rem; color: #3D4596;'>{CHARITY['heading']}</h1>"
    f"{_lines}</div>"})
for n, (title, sub) in zip((5, 4, 3, 2, 1), PRIZES):
    slides.append({"id": f"prize-{n}", "type": "info", "title": f"Prize #{n}",
                   "htmlContent": f"<div class='prize-single'><h2>{title}</h2>" + (f"<p class='prize-subtext'>{sub}</p>" if sub else "") + "</div>"})
slides += mcq_round(1, R1) + audio_round(2, R2) + video_round(3, R3, "music videos")
def ranked(scores):
    """Competition ranking (1, 1, 1, 4, ...) keeping sheet order inside a tie."""
    srt = sorted(scores, key=lambda t: -t[1]); out = []
    for i, (name, pts) in enumerate(srt):
        rank = out[-1][0] if out and out[-1][2] == pts else i + 1
        out.append((rank, name, pts))
    return out

def ordinal(n): return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"

def score_slides(prefix, scores, top_places=5, per_list=7):
    """Reveal slides for every score group placed in the top `top_places` (lowest first), then position lists."""
    from html import escape
    r = ranked(scores); counts = {}
    for rank, _, _ in r: counts[rank] = counts.get(rank, 0) + 1
    top = [g for g in dict.fromkeys(rank for rank, _, _ in r) if g <= top_places]
    out = []
    for g in reversed(top):
        teams = [(n, p) for rank, n, p in r if rank == g]
        names = "".join(f"<div style='font-size: {1.5 if len(teams) == 1 else 1.15}em; font-weight: bold; color: #FA1302; margin-top: 0.15em;'>{escape(n)}</div>" for n, _ in teams)
        title = f"{'Joint ' if len(teams) > 1 else ''}{ordinal(g)} Place"
        out.append({"id": f"{prefix}-{ordinal(g)}", "type": "info", "title": title,
                    "htmlContent": f"<div style='text-align: center; font-size: 3em; margin-top: 0.6em;'>{names}"
                                   f"<div style='font-size: 0.8em; margin-top: 0.5em; color: #888;'>{teams[0][1]} points</div></div>"})
    rest = [t for t in r if t[0] > max(top, default=0)]
    chunks, cur = [], []  # break only between score groups, so a tie never spans two slides
    for rank in dict.fromkeys(t[0] for t in rest):
        group = [t for t in rest if t[0] == rank]
        if cur and len(cur) + len(group) > per_list:
            chunks.append(cur); cur = []
        cur += group
    if cur: chunks.append(cur)
    if len(chunks) > 1 and len(chunks[-1]) <= 2:  # don't leave one or two teams alone on a slide
        chunks[-2] += chunks.pop()
    for k, chunk in enumerate(chunks):
        lines = "".join(f"<div>{f'{rank}=' if counts[rank] > 1 else f'{rank}.'} {escape(n)} &middot; {p}</div>" for rank, n, p in chunk)
        out.append({"id": f"{prefix}-rest-{k + 1}", "type": "info",
                    "title": f"Positions {chunk[0][0]}&ndash;{chunk[-1][0]}",
                    "htmlContent": f"<div style='text-align: center; font-size: 2.5em; line-height: 1.55; color: #ddd;'>{lines}</div>"})
    return out

if HALFTIME:
    slides += [copy.deepcopy(T["halftime"]), copy.deepcopy(T["halftime-intro"])] + score_slides("halftime", HALFTIME)
else:
    slides += blank_scores([s["id"] for s in tpl["slides"] if s["id"].startswith("halftime")])
slides += mcq_round(4, R4) + picture_round(5, R5) + video_round(6, R6, "videos")
def final_slides(scores, n_prizes=5):
    """Prize places 5th -> 1st. A tie on a prize place gets one 'Tie for Nth Place' slide (sudden death is run live),
    preceded by the prize(s) that tie decides. Then the rest of the table, THE END and the thank-you."""
    from html import escape
    r = ranked(scores); counts = {}
    for rank, _, _ in r: counts[rank] = counts.get(rank, 0) + 1
    groups = [g for g in dict.fromkeys(rank for rank, _, _ in r) if g <= n_prizes]
    prize_line = lambda place: (lambda t, s: f"<div style='margin-top: 0.7em;'><div style='font-size: 1.6em; font-weight: bold; color: #FA1302;'>{ordinal(place)}: {t}</div>"
        + "".join(f"<div style='font-size: 1.3em; color: #ccc; margin-top: 0.3em;'>{part.replace('<br>', ' ')}</div>" for part in (s.split('<br><br>') if s else [])) + "</div>")(*PRIZES[n_prizes - place])
    out = [copy.deepcopy(T["grading"])]
    for g in reversed(groups):
        teams = [(n, p) for rank, n, p in r if rank == g]
        places = [pl for pl in range(g, g + len(teams)) if pl <= n_prizes]
        label = " &amp; ".join(ordinal(pl) for pl in reversed(places))
        out.append({"id": f"final-{ordinal(g)}-place", "type": "info", "title": f"{label} Place" + (" Prizes" if len(places) > 1 else ""),
                    "htmlContent": "<div style='text-align: center; margin-top: 0.3em; font-size: 2em; line-height: 1.3;'>" + "".join(prize_line(pl) for pl in reversed(places)) + "</div>"})
        names = "".join(f"<div style='font-size: {1.5 if len(teams) == 1 else 1.15}em; font-weight: bold; color: #FA1302; margin-top: 0.15em;'>{escape(n)}</div>" for n, _ in teams)
        tie = len(teams) > 1
        out.append({"id": f"final-{ordinal(g)}-team", "type": "info", "title": f"Tie for {ordinal(g)} Place!" if tie else f"{ordinal(g)} Place",
                    "htmlContent": f"<div style='text-align: center; font-size: 3em; margin-top: 0.4em;'>{names}"
                                   f"<div style='font-size: 0.8em; margin-top: 0.5em; color: #888;'>{teams[0][1]} points</div>"
                                   + ("<div style='font-size: 0.9em; margin-top: 0.6em; font-weight: bold; color: #FFFFFF;'>Sudden death tiebreaker!</div>" if tie else "")
                                   + "</div>"})
        if tie and TIE_WINNERS.get(g):  # winner of the live sudden death
            w = TIE_WINNERS[g]
            out.append({"id": f"final-{ordinal(g)}-winner", "type": "info", "title": f"{ordinal(g)} Place",
                        "htmlContent": f"<div style='text-align: center; font-size: 3em; margin-top: 0.4em;'>"
                                       f"<div style='font-size: {1.9 if g == 1 else 1.5}em; font-weight: bold; color: #FA1302;'>{escape(w)}</div>"
                                       f"<div style='font-size: 0.8em; margin-top: 0.5em; color: #888;'>{teams[0][1]} points &middot; won the sudden death</div></div>"})
    last_prize_rank = max(groups)
    rest_scores = [(n, p) for rank, n, p in r if rank > last_prize_rank]
    rest = score_slides("final", rest_scores, top_places=0) if rest_scores else []
    offset = len(r) - len(rest_scores)  # renumber the rest so positions continue after the prize places
    for s in rest:
        s["title"] = re.sub(r"\d+", lambda m: str(int(m.group()) + offset), s["title"])
        s["htmlContent"] = re.sub(r"<div>(\d+)", lambda m: f"<div>{int(m.group(1)) + offset}", s["htmlContent"])
    return out + rest + [copy.deepcopy(T["final-end"]), copy.deepcopy(T["final-thank-you"])]

if FINAL:
    slides += final_slides(FINAL)
else:
    slides += blank_scores([s["id"] for s in tpl["slides"] if s["id"] == "grading" or s["id"].startswith("final-")])
for s in slides:
    if s["id"] == "final-thank-you":
        s["subtitle"] = "to the 7th Nostalgia Quiz Night<br>we hope you had a fantastic time"
        s["message"] = f'Quiz Night #7\n{SETTINGS["venue"]}'
    if s["id"].startswith("final-") and s["id"].endswith("-place") and "Prize:" in s.get("htmlContent", ""):
        rank = int(s["id"].split("-")[1][0]); title, sub = PRIZES[5 - rank]
        main, _, extra = sub.partition("<br><br>")  # text after a blank line goes on its own block
        sub_line = f"<div style='font-size: 1.3em; color: #bbb; margin-top: 0.4em;'>{main.replace('<br>', ' ')}</div>" if sub else ""
        if extra:
            sub_line += f"<div style='font-size: 1.3em; color: #bbb; margin-top: 0.6em;'>{extra}</div>"
        s["htmlContent"] = f"<div style='text-align: center; margin-top: 1em;'><div style='font-size: 2.6em; font-weight: bold; color: #FA1302; margin-top: 0.5em;'>Prize: {title}</div>{sub_line}</div>"

cfg = copy.deepcopy(tpl); cfg["settings"].update(SETTINGS); cfg["slides"] = slides
cfg["settings"]["theme"].update(THEME)
txt = json.dumps(cfg, ensure_ascii=False)
for old, new in (("#E5EA6F", THEME["accentColor"]), ("#FA1302", THEME["secondaryAccent"])):
    txt = txt.replace(old, new).replace(old.lower(), new)
cfg = json.loads(txt)
# Eric 2026-10-15: no "round" in intro subtitles, no trailing period on instructions, "HALF TIME BREAK"
for s in cfg["slides"]:
    if s["type"] == "round-intro":
        s["subtitle"] = s.get("subtitle", "").replace(" round)", ")")
        s["instructions"] = s.get("instructions", "").rstrip().rstrip(".")
    if s["id"] == "round5-intro":  # R5 is all album covers (2026-10-15)
        s["subtitle"] = "(album covers)"
        s["instructions"] = "Name the artist and the album for each cover"
    if s["id"] == "halftime":
        s["title"] = "HALF TIME BREAK"; s.pop("subtitle", None)
for s in cfg["slides"]:
    if s["id"] == "grading": s["image"] = "welcome.jpg"  # logo sits high, leaving room for the title
# Live-event resume: START_FROM=<slide id> drops everything before it, so a reload opens on that slide.
# Run the builder again WITHOUT it to restore the full show.
if os.environ.get("START_FROM"):
    ids = [s["id"] for s in cfg["slides"]]
    cfg["slides"] = cfg["slides"][ids.index(os.environ["START_FROM"]):]
    refs = {s["id"] for s in cfg["slides"]}
    assert all(s.get("questionRefId", s["id"]) in refs for s in cfg["slides"]), "answer slide lost its question"
ids = [s["id"] for s in cfg["slides"]]; assert len(ids) == len(set(ids)), "duplicate slide ids"
json.dump(cfg, open(os.path.join(APP, "quiz-config.json"), "w"), ensure_ascii=False, indent=2)
print(len(slides), "slides;", sum(1 for s in slides if s["id"].endswith("-todo")), "round placeholders")
