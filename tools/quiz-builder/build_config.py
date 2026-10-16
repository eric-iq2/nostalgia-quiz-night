#!/usr/bin/env python3
"""Build Quiz #7 quiz-config.json from the #6 config as a template.
Rounds with no data yet render as a clearly-marked placeholder slide.
Usage: python3 build_config.py   (writes ../nostalgia-quiz-night/quiz-config.json)"""
import json, copy, os
from rounds import R1, R2, R3, R4, R5, R6, SETTINGS, PRIZES, THEME

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
for n, (title, sub) in zip((5, 4, 3, 2, 1), PRIZES):
    slides.append({"id": f"prize-{n}", "type": "info", "title": f"Prize #{n}",
                   "htmlContent": f"<div class='prize-single'><h2>{title}</h2>" + (f"<p class='prize-subtext'>{sub}</p>" if sub else "") + "</div>"})
slides += mcq_round(1, R1) + audio_round(2, R2) + video_round(3, R3, "music videos")
slides += blank_scores([s["id"] for s in tpl["slides"] if s["id"].startswith("halftime")])
slides += mcq_round(4, R4) + picture_round(5, R5) + video_round(6, R6, "videos")
slides += blank_scores([s["id"] for s in tpl["slides"] if s["id"] == "grading" or s["id"].startswith("final-")])
for s in slides:
    if s["id"] == "final-thank-you":
        s["subtitle"] = "to the 7th Nostalgia Quiz Night<br>we hope you had a fantastic time"
        s["message"] = f'Quiz Night #7\n{SETTINGS["venue"]}'
    if s["id"].startswith("final-") and s["id"].endswith("-place") and "Prize:" in s.get("htmlContent", ""):
        rank = int(s["id"].split("-")[1][0]); title, sub = PRIZES[5 - rank]
        sub_line = f"<div style='font-size: 1.3em; color: #bbb; margin-top: 0.4em;'>{sub.replace('<br>', ' ')}</div>" if sub else ""
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
ids = [s["id"] for s in slides]; assert len(ids) == len(set(ids)), "duplicate slide ids"
json.dump(cfg, open(os.path.join(APP, "quiz-config.json"), "w"), ensure_ascii=False, indent=2)
print(len(slides), "slides;", sum(1 for s in slides if s["id"].endswith("-todo")), "round placeholders")
