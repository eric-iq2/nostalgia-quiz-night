You are an expert front-end engineer and UI designer.
Your task is to build a browser-based quiz slideshow that replaces a Keynote presentation for a live quiz night.

I will attach reference screenshots from my current Keynote deck with this prompt.
Use them as visual inspiration (colors, fonts, layout, style), but you don’t need to clone them pixel-perfect.

⸻

HIGH-LEVEL GOAL

Create a single-page web app that:
	•	Runs in a browser (Chrome on macOS, 16:9 projector).
	•	Behaves like a slide deck (Keynote/PowerPoint):
	•	Navigate forward/backward with the keyboard.
	•	Shows different screens: welcome, questions, answers, leaderboards, thank you, etc.
	•	Is fully driven by a JSON config file:
	•	All rounds, slides, questions, answers, media and settings come from that JSON.
	•	I will edit the JSON for each new quiz; I don’t want to touch the code.

This is display-only: teams answer on paper; the website just shows content.

⸻

TECH REQUIREMENTS
	1.	Stack
	•	Plain HTML + CSS + vanilla JavaScript.
	•	No frameworks (no React/Vue/Angular, no build tools).
	•	Everything should work by opening index.html from a simple static server in Chrome.
	2.	Files & structure
Create this structure:
	•	index.html
	•	styles.css
	•	app.js
	•	quiz-config.example.json
	•	README.md
	•	(Optionally) media/ folder with placeholder file names referenced in the example JSON.
I will later:
	•	Duplicate quiz-config.example.json as quiz-config.json,
	•	Put real media files (videos, audio, images) into media/.
	3.	Config loading
	•	The app should fetch('quiz-config.json') by default.
	•	If that fails, it can fall back to quiz-config.example.json.
	•	Show a clear on-screen error message if the config can’t be loaded.
In the README, explain that I should run a simple local HTTP server (e.g. python -m http.server) instead of opening index.html directly via file://, to avoid CORS issues with fetch.

⸻

USER INTERFACE & DISPLAY
	1.	Fullscreen mode
	•	Fullscreen toggle:
	•	F key toggles fullscreen.
	•	A small fullscreen button in the top-right corner does the same.
	•	Use the standard DOM Fullscreen API (document.documentElement.requestFullscreen(), document.exitFullscreen()).
	•	Show a subtle icon or label (e.g. “⤢ Fullscreen” / “⤢ Exit Fullscreen”) that matches the visual style.
	2.	Controls overlay
	•	There should be a subtle control bar top-right (host-facing), with:
	•	“Prev” and “Next”
	•	Current slide / total slides (e.g. Slide 5 / 42)
	•	Fullscreen toggle icon
	•	Behavior:
	•	Hidden by default during presentation.
	•	Appears when:
	•	Mouse moves
	•	Or mouse hovers near the top edge of the screen.
	•	Fades out again after ~3 seconds of no mouse movement.
	•	Controls should be large enough to click from a distance but visually unobtrusive.
	3.	Slide layout
General rules:
	•	Optimized for 16:9 landscape on a projector.
	•	Text: large, high-contrast, easy to read from the back of a room.
	•	Center content by default (vertically and horizontally), unless layout demands otherwise.
	•	Use a simple, clean font stack (e.g. system fonts) unless the screenshots clearly suggest something else.
	•	Use theme colors from JSON (see config spec below).

⸻

KEYBOARD CONTROLS

Implement at least:
	•	Right Arrow or Space → Next slide
	•	Left Arrow → Previous slide
	•	F → Toggle fullscreen
	•	S → Skip: on a question slide, skip immediately to countdown video (see below)
	•	R → Restart the question timer for the current slide (if that slide uses timing)

Behavior details:
	•	Any navigation key (next/prev) should:
	•	Cancel any running question timer.
	•	Stop and hide any playing countdown video.
	•	If R is pressed on a slide without a question timer, do nothing (or a no-op).

⸻

SLIDE FLOW, TIMERS & COUNTDOWN

This is the critical behavior:
	1.	Question duration
	•	For any slide that is a “question”:
	•	When the slide becomes active:
	•	Start a question timer.
	•	By default, the timer length is settings.defaultQuestionDurationSec from JSON (usually 30 seconds).
	•	A slide can override this with timerSeconds.
	•	Optional visual: show a small countdown on-screen (e.g. in a corner or under the question). Keep it subtle but readable.
	2.	Countdown video
	•	After the question timer expires:
	1.	Automatically overlay a global countdown video over the slide.
	2.	The countdown video path comes from JSON: settings.countdownVideo.
	3.	The video should:
	•	Play with sound.
	•	Be centered and large (can be nearly full-screen).
	•	Darken/dim the background slide while it plays.
	4.	When the countdown video ends:
	•	Automatically hide the video overlay.
	•	Automatically advance to the next slide in the deck.
	•	The same countdown clip is used for all question slides by default.
	3.	Skip & restart
	•	S key: while on a question slide:
	•	Immediately start the countdown video (as if the question timer had expired).
	•	Ignore any remaining question time.
	•	R key: while on a question slide:
	•	Reset and restart the question timer from full duration.
	•	If the countdown video is currently playing, R should not do anything (or it should restart the question phase only if you choose a simple consistent behavior; document it in comments).
	4.	Non-question slides
	•	Non-question slides (welcome, round intro, leaderboard, answers, thank you) should not automatically start timers or countdown videos.
	•	They advance only via keyboard or UI controls.

⸻

JSON CONFIG SPEC

The entire quiz is configured by a single JSON file.

Create a sample configuration file called quiz-config.example.json that demonstrates:
	•	A welcome slide
	•	Round 1:
	•	One or two MCQ questions
	•	One free-text question
	•	A leaderboard slide
	•	Round 3:
	•	One video-based question
	•	Round 6:
	•	One audio-based question
	•	A final “thank you” slide

Top-level structure
Use this shape:

{
  "settings": {
    "title": "Quiz Night",
    "defaultQuestionDurationSec": 30,
    "countdownVideo": "media/countdown_10s.mp4",
    "theme": {
      "backgroundColor": "#000000",
      "textColor": "#ffffff",
      "accentColor": "#ffcc00",
      "fontFamily": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    }
  },
  "slides": [
    // array of slide objects (see below)
  ]
}

Slide order
	•	slides is a flat array.
	•	The deck is shown strictly in order of this array.
	•	Each slide may have an optional round property (1–6) to indicate which round it belongs to; this is mostly for my own organization but you can display it where appropriate (e.g. on round intro slides).

Common slide fields
Each slide object:

{
  "id": "unique-string-id",
  "type": "one-of-the-types-below",
  "round": 1,           // optional, number 1–6
  "notes": "Host-only notes shown nowhere" // optional, ignored by renderer
}

Slide types
Implement these slide types:
	1.	Welcome slide

{
  "id": "welcome",
  "type": "welcome",
  "title": "Welcome to Quiz Night!",
  "subtitle": "Grab a drink, grab a pen.",
  "logoImage": "media/logo.png"
}

	•	Show title, subtitle, and optional logo image.

	2.	Round intro

{
  "id": "round1-intro",
  "type": "round-intro",
  "round": 1,
  "title": "Round 1 – General Knowledge",
  "subtitle": "10 multiple choice questions + 2 bonus"
}

	•	Large round title; optional subtitle.
	•	No timer or countdown.

	3.	Multiple-choice question

{
  "id": "r1-q1",
  "type": "question-mcq",
  "round": 1,
  "questionNumber": 1,
  "questionText": "What is the capital of France?",
  "options": [
    "Berlin",
    "Madrid",
    "Paris",
    "Rome"
  ],
  "correctOptionIndex": 2,
  "timerSeconds": 30,       // optional; default from settings if missing
  "image": "media/r1_q1.jpg" // optional image to show alongside question
}

	•	Layout:
	•	Question text big and clear.
	•	Options labeled A, B, C, D automatically.
	•	If image is provided, show it nicely alongside/above the question.

	4.	Free-text question

{
  "id": "r1-bonus1",
  "type": "question-free-text",
  "round": 1,
  "questionNumber": "Bonus 1",
  "questionText": "Name any country that borders France.",
  "correctAnswerText": "Belgium, Luxembourg, Germany, Switzerland, Italy, Monaco, Spain, Andorra",
  "timerSeconds": 45,
  "image": null
}

	•	Same timer behavior as MCQ.
	•	correctAnswerText is used later on the answer slide (see below).

	5.	Video question (Round 3 style)

{
  "id": "r3-q1",
  "type": "question-video",
  "round": 3,
  "questionNumber": 1,
  "questionText": "Name the movie.",
  "videoSrc": "media/round3/q1_clip.mp4",
  "autoplay": true,
  "loop": false,
  "timerSeconds": 30
}

	•	Show the question text and the video.
	•	When the slide loads:
	•	If autoplay is true, start the video automatically after the user has interacted with the page at least once (to satisfy Chrome autoplay policies).
	•	User interaction counts as any key press or click during the session.

	6.	Audio question (Round 6 style)

{
  "id": "r6-q1",
  "type": "question-audio",
  "round": 6,
  "questionNumber": 1,
  "questionText": "Name the artist.",
  "audioSrc": "media/round6/q1_clip.mp3",
  "autoplay": true,
  "timerSeconds": 30
}

	•	Show question text and an audio player UI (custom or browser default, but styled).
	•	Respect autoplay rules similarly to the video questions.

	7.	Answer slide

{
  "id": "r1-q1-answer",
  "type": "answer",
  "round": 1,
  "questionRefId": "r1-q1",
  "title": "Answer 1",
  "extraText": "The capital of France is Paris."
}

Behavior:
	•	The renderer should:
	•	Look up the referenced question slide by questionRefId.
	•	Show the original question text.
	•	For MCQ questions:
	•	Show all options again, with the correct one clearly highlighted.
	•	For free-text/video/audio questions:
	•	Show correctAnswerText from the original question slide, if present.
	•	Also show any extraText from this answer slide.
	•	No timers or countdown on answer slides.

	8.	Leaderboard

{
  "id": "r1-leaderboard",
  "type": "leaderboard",
  "round": 1,
  "title": "Scores after Round 1",
  "teams": [
    { "name": "Table 1", "score": 12 },
    { "name": "Table 2", "score": 10 },
    { "name": "Table 3", "score": 8 }
  ]
}

	•	Display a simple table of team names and scores.
	•	Sort by score descending before rendering.

	9.	Info / break slide (generic text/image)

{
  "id": "break1",
  "type": "info",
  "title": "Half Time Break",
  "subtitle": "Top up your drinks, we start again in 10 minutes.",
  "image": "media/beer.png"
}

	10.	Thank you slide

{
  "id": "thanks",
  "type": "thank-you",
  "title": "Thanks for playing!",
  "subtitle": "See you next time."
}


⸻

APP LOGIC & ARCHITECTURE (app.js)

Implement the app logic in a clean, modular way.

Key points:
	1.	State
	•	Keep track of:
	•	slides array
	•	currentSlideIndex
	•	currentQuestionTimer (timeout ID)
	•	countdownVideoElement
	•	isCountdownPlaying
	•	On slide change:
	•	Clear any existing timers.
	•	Stop/hide any countdown video.
	•	Render the new slide.
	2.	Rendering
	•	Have a main container <div id="slide-root"></div> in index.html.
	•	In app.js, based on slide.type, call a renderer function:
	•	renderWelcome(slide)
	•	renderRoundIntro(slide)
	•	renderQuestionMcq(slide)
	•	renderQuestionFreeText(slide)
	•	renderQuestionVideo(slide)
	•	renderQuestionAudio(slide)
	•	renderAnswer(slide)
	•	renderLeaderboard(slide)
	•	renderInfo(slide)
	•	renderThankYou(slide)
	•	Each renderer:
	•	Clears existing content.
	•	Creates DOM elements.
	•	Applies CSS classes that you define in styles.css.
	3.	Timers & countdown integration
	•	For question slide renderers, after rendering:
	•	Call a shared startQuestionTimer(slide) if timerSeconds or default is set.
	•	startQuestionTimer:
	•	Shows visible countdown on screen (e.g. small timer text).
	•	Uses setTimeout for the full timer duration.
	•	When it fires, calls startCountdownVideoThenAdvance().
	•	startCountdownVideoThenAdvance():
	•	Shows the global countdown video overlay.
	•	Sets its src from settings.countdownVideo.
	•	Plays the video (ensuring user has interacted at least once earlier in the session).
	•	On ended event:
	•	Hides the overlay.
	•	Calls goToNextSlide().
	4.	Keyboard handler
	•	Attach a single keydown handler on document.
	•	Handle keys:
	•	Left Arrow → goToPreviousSlide()
	•	Right Arrow / Space → goToNextSlide()
	•	F → toggle fullscreen
	•	S → if current slide is a question type, startCountdownVideoThenAdvance() (skipping the remaining timer)
	•	R → if current slide is a question type, restart its timer
	5.	Resilience
	•	If questionRefId on an answer slide doesn’t match any slide, show a clear warning on screen.
	•	If media files can’t load (video/audio/image error events), show a small warning area instead of breaking the app.
	6.	Comments & readability
	•	Add clear comments, especially around:
	•	Timer & countdown logic
	•	Keyboard handling
	•	How slide types map to UI

⸻

STYLING (styles.css)
	•	Use CSS to:
	•	Center and scale content appropriately for a projector.
	•	Implement show/hide + fade of the control overlay.
	•	Style MCQ options with clear labels (A/B/C/D).
	•	Highlight the correct MCQ answer on answer slides (e.g. accent color background).
	•	Format the leaderboard table cleanly and legibly.
	•	Make sure the app looks professional and clean even without my screenshots, but try to take cues from the screenshots I’ll provide:
	•	Color palette
	•	General “feel” (minimal/retro/fun/etc.)
	•	Any particular layout for question vs answer slides.

⸻

README

In README.md, explain briefly:
	•	What the project is.
	•	How to run it locally (e.g. python -m http.server then open http://localhost:8000).
	•	How to create a new quiz by copying quiz-config.example.json to quiz-config.json and editing:
	•	Slides
	•	Question text
	•	Options
	•	Media file paths
	•	Answers
	•	Leaderboards
	•	A quick reference of slide types and their JSON fields.

⸻

Deliverables

Please output:
	1.	index.html (with <link> to styles.css, <script> for app.js, and basic layout/containers)
	2.	styles.css
	3.	app.js
	4.	quiz-config.example.json with realistic example content
	5.	README.md

Make sure the code is valid, consistent, and ready to drop into a folder and run (once I add my real quiz-config.json and media files).

