# Quiz Night Browser Slideshow

A browser-based quiz slideshow application that replaces traditional Keynote/PowerPoint presentations for live quiz nights. Navigate through questions, display multimedia content, and show leaderboards—all controlled by simple keyboard commands.

## Features

- **Fully Browser-Based**: Runs in Chrome on macOS, optimized for 16:9 projectors
- **JSON-Driven Configuration**: All quiz content, media, and settings defined in a single JSON file
- **Multiple Slide Types**: Questions (MCQ, free-text, video, audio), answers, leaderboards, round intros, and more
- **Question Timers**: Automatic countdown timers with visual countdown videos
- **Keyboard Controls**: Navigate slides, skip timers, and toggle fullscreen
- **No Build Tools**: Pure HTML, CSS, and vanilla JavaScript

## Quick Start

### 1. Set Up Your Quiz

1. Copy the example configuration:
   ```bash
   cp quiz-config.example.json quiz-config.json
   ```

2. Add your media files to the `media/` folder (videos, audio, images)

3. Edit `quiz-config.json` to customize your quiz content

### 2. Run Locally

You need a local HTTP server to avoid CORS issues with loading JSON and media files.

**Using Python 3:**
```bash
python3 -m http.server 8000
```

**Using Python 2:**
```bash
python -m SimpleHTTPServer 8000
```

**Using Node.js (if you have `http-server` installed):**
```bash
npx http-server -p 8000
```

### 3. Open in Browser

Navigate to:
```
http://localhost:8000
```

Press **F** to enter fullscreen mode and start your quiz!

## Keyboard Controls

| Key | Action |
|-----|--------|
| **→** or **Space** | Next slide |
| **←** | Previous slide |
| **F** | Toggle fullscreen |
| **S** | Skip to countdown video (on question slides) |
| **R** | Restart question timer (on question slides) |

## Configuration Guide

The entire quiz is configured via `quiz-config.json`. Here's the structure:

### Top-Level Structure

```json
{
  "settings": {
    "title": "Quiz Night",
    "defaultQuestionDurationSec": 30,
    "countdownVideo": "media/countdown_10s.mp4",
    "theme": {
      "backgroundColor": "#1a1a2e",
      "textColor": "#ffffff",
      "accentColor": "#ffcc00",
      "fontFamily": "system-ui, sans-serif"
    }
  },
  "slides": [ /* array of slide objects */ ]
}
```

### Slide Types

#### 1. Welcome Slide
```json
{
  "id": "welcome",
  "type": "welcome",
  "title": "Welcome to Quiz Night!",
  "subtitle": "Grab a drink, grab a pen.",
  "logoImage": "media/logo.png"
}
```

#### 2. Round Intro
```json
{
  "id": "round1-intro",
  "type": "round-intro",
  "round": 1,
  "title": "Round 1 – General Knowledge",
  "subtitle": "10 multiple choice questions"
}
```

#### 3. Multiple Choice Question (MCQ)
```json
{
  "id": "r1-q1",
  "type": "question-mcq",
  "round": 1,
  "questionNumber": 1,
  "questionText": "What is the capital of France?",
  "options": ["Berlin", "Madrid", "Paris", "Rome"],
  "correctOptionIndex": 2,
  "timerSeconds": 30,
  "image": "media/r1_q1.jpg"
}
```

#### 4. Free-Text Question
```json
{
  "id": "r1-bonus1",
  "type": "question-free-text",
  "round": 1,
  "questionNumber": "Bonus 1",
  "questionText": "Name any country that borders France.",
  "correctAnswerText": "Belgium, Luxembourg, Germany, Switzerland, Italy, Monaco, Spain, Andorra",
  "timerSeconds": 45
}
```

#### 5. Video Question (Round 3 Style)
```json
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
```

#### 6. Audio Question (Round 6 Style)
```json
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
```

#### 7. Answer Slide
```json
{
  "id": "r1-q1-answer",
  "type": "answer",
  "round": 1,
  "questionRefId": "r1-q1",
  "title": "Answer 1",
  "extraText": "Additional explanation or fun facts."
}
```

The answer slide automatically looks up the question by `questionRefId` and displays:
- For MCQ: All options with the correct one highlighted
- For other questions: The `correctAnswerText` from the original question

#### 8. Leaderboard
```json
{
  "id": "r1-leaderboard",
  "type": "leaderboard",
  "round": 1,
  "title": "Scores after Round 1",
  "teams": [
    { "name": "Table 1", "score": 12 },
    { "name": "Table 2", "score": 10 }
  ]
}
```

Teams are automatically sorted by score (descending).

#### 9. Info/Break Slide
```json
{
  "id": "break1",
  "type": "info",
  "title": "Half Time Break",
  "subtitle": "Back in 10 minutes!",
  "image": "media/beer.png"
}
```

#### 10. Thank You Slide
```json
{
  "id": "thanks",
  "type": "thank-you",
  "title": "Thanks for playing!",
  "subtitle": "See you next time."
}
```

## How Question Timers Work

1. When a question slide appears, a countdown timer starts (default 30 seconds, configurable per-slide)
2. A visual timer appears in the bottom-right corner
3. When time expires, a countdown video automatically plays
4. After the video ends, the app advances to the next slide
5. You can skip directly to the countdown by pressing **S**
6. You can restart the timer by pressing **R**

## Countdown Video

The global countdown video is defined in `settings.countdownVideo`. This plays after every question timer expires. Make sure to:
- Use a video format supported by Chrome (MP4 with H.264 is recommended)
- Keep it short (typically 5-10 seconds)
- Include audio for dramatic effect!

## Media Files

Place all media files in the `media/` folder:
```
media/
├── countdown_10s.mp4   (countdown video)
├── logo.png            (welcome screen logo)
├── round3/
│   ├── clip1.mp4       (video questions)
│   └── clip2.mp4
└── round6/
    ├── song1.mp3       (audio questions)
    └── song2.mp3
```

Reference them in your JSON using relative paths like `"media/logo.png"`.

## Customization

### Theme Colors

Customize the look in `settings.theme`:
- `backgroundColor`: Main background color
- `textColor`: Primary text color
- `accentColor`: Highlights, timers, and accents
- `fontFamily`: Font stack

### Slide Order

Slides appear in the exact order they're defined in the `slides` array. Organize them however you like!

### Timer Durations

- Set a default timer: `settings.defaultQuestionDurationSec`
- Override per-question: `timerSeconds` on any question slide

## Browser Compatibility

- **Recommended**: Chrome on macOS (fullscreen API support)
- **Resolution**: Optimized for 16:9 aspect ratio (1920×1080, 1280×720)

## Troubleshooting

**Config file won't load:**
- Make sure you're using a local HTTP server (not `file://` protocol)
- Check browser console for errors

**Media files won't play:**
- Verify file paths in your JSON
- Ensure files exist in the `media/` folder
- Check file formats (MP4 for video, MP3/WAV for audio)

**Autoplay not working:**
- The first interaction (any keypress or click) enables autoplay
- This is a browser security feature

## Credits

Built with vanilla JavaScript—no frameworks, no build tools, just web standards.

Perfect for pub quizzes, trivia nights, and any presentation where you need interactive question timing!
