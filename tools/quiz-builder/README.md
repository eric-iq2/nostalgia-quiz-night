# Quiz builder

Generates `quiz-config.json` for a quiz night. It was written for Quiz #7 (16 Oct 2026).

```bash
cd tools/quiz-builder && python3 build_config.py   # writes ../../quiz-config.json
```

- `rounds.py` holds the content: settings, theme, prizes and the six rounds (`R1`–`R6`). Each question gives its point labels (`parts`), the answer and an optional grey note.
- `mc.json` holds the multiple-choice rounds (R1, R4), parsed from the Google Sheet.
- `q6-template.json` is the Quiz #6 config. It supplies the fixed slides (welcome, round intros, collection, half-time and final reveals), which the builder copies and restyles.
- Media is positional. Question N of round R uses `media/rR-qN.{mp3,mp4,jpg}`. If you reorder a round, renumber the files too.
- A round left empty (`[]`) renders as a "⚠ Round N — not added yet" slide, so half-built quizzes can't be mistaken for finished ones.
- House style applied automatically:
  - no "round" in intro subtitles, e.g. "(sounds)"
  - no trailing period on instructions
  - "HALF TIME BREAK"
  - prize line on the final reveal slides at 2.6em

For the next quiz: copy the current `quiz-config.json` to a new template, swap in the new content in `rounds.py` / `mc.json`, and pick a new `THEME`.
