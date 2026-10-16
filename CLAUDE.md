# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

This is a static web application with no build process. To run it locally:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000` in Chrome. A local HTTP server is required to avoid CORS issues when loading JSON and media files.

**Important**: Never use `file://` protocol - fetch() calls will fail.

## Architecture Overview

This is a vanilla JavaScript slideshow application with three core files:

- `index.html` - Static DOM structure with containers
- `app.js` - All application logic (~1020 lines)
- `styles.css` - All styling
- `quiz-config.json` - Quiz content (user creates from `quiz-config.example.json`)

### Application State Management

State is centralized in the `state` object (app.js:7-16):
- `config` - Loaded JSON configuration
- `slides` - Array of slide objects from config
- `currentSlideIndex` - Current position in slides array
- `currentQuestionTimer` - setTimeout ID for question timers
- `isCountdownPlaying` - Prevents timer restart during countdown
- `hasUserInteracted` - Required for autoplay compliance

All DOM elements are cached in the `elements` object (app.js:18-29) during initialization.

### Slide Rendering Architecture

The application uses a type-based renderer pattern:

1. `renderCurrentSlide()` (app.js:190-243) is the entry point
2. Clears existing timers/countdown before rendering
3. Routes to specific renderer based on `slide.type` via switch statement
4. Each slide type has a dedicated renderer function (e.g., `renderQuestionMcq()`)

**16 Slide Types**:
- `welcome`, `round-intro`, `question-mcq`, `question-free-text`, `question-video`, `question-audio`, `answer`, `leaderboard`, `info`, `thank-you`
- Media-round trio, used by Quizzes #6–#7 for pictures and videos: `picture-question` → `picture-fullscreen` → `picture-timer`, and `video-clip` → `video-fullscreen` → `video-clip-timer`. Answer slides for these point their `questionRefId` at the `*-timer` slide, which carries `correctAnswerText`.

Line numbers quoted elsewhere in this file date from the 682-line version and are approximate. Search for the function name instead.

### Question Timer System

Question slides automatically trigger timers via `startQuestionTimer()` (app.js:561-604):

1. Timer duration from `slide.timerSeconds` or `settings.defaultQuestionDurationSec` (default 30s)
2. Creates visual timer display (bottom-right corner, circular)
3. Updates every second via `setInterval`
4. Plays looping countdown audio tick during last 10 seconds (requires user interaction first)
5. When timer expires, calls `showTimesUp()` which:
   - Hides all answer options (MCQ choices or free-text prompts)
   - Displays "TIME'S UP!" message with animation
   - Auto-advances to next slide after 3 seconds

**Critical Behavior**: Navigation (next/prev) or new slide render must call `clearQuestionTimer()` to prevent timer leaks.

**Audio**: Countdown tick audio (`media/countdown-tick.wav` or `.mp3`) loops during final 10 seconds at 30% volume.

### Answer Slide Cross-Reference System

Answer slides (type: `answer`) use `questionRefId` to look up the original question slide (app.js:424):

```javascript
const questionSlide = state.slides.find(s => s.id === slide.questionRefId);
```

- For MCQ: Re-renders options with `.correct` class on correct answer
- For other types: Displays `correctAnswerText` from question slide
- If `questionRefId` not found, shows warning instead of crashing

### Configuration Loading

`loadConfig()` (app.js:57-82) tries to fetch in order:
1. `quiz-config.json` (user's quiz)
2. `quiz-config.example.json` (fallback)

After loading, calls `applyTheme()` (app.js:85-105) which applies theme colors from `settings.theme` to DOM via inline styles and CSS custom properties.

## JSON Configuration Structure

All quiz content comes from a single JSON file. Key points:

- `settings.countdownAudio` - Audio tick that plays during final 10 seconds of question timers
- `settings.defaultQuestionDurationSec` - Default timer for all questions (typically 30s)
- `settings.theme` - Colors and fonts applied via JavaScript
- `slides` - Flat array in display order (not grouped by round)

Question slides support optional `timerSeconds` override. MCQ options are always labeled A/B/C/D automatically (app.js:304).

**Quiz Structure Pattern**: Each round follows this sequence:
1. Round intro slide
2. All questions for the round (10 MCQ + 2 bonus)
3. All answers grouped together (12 answer slides)
4. "End of Round X" info slide
5. Break slide (between rounds)

## Building a quiz config

`quiz-config.json` is generated, not hand-edited. See `tools/quiz-builder/README.md`: `python3 build_config.py` assembles the slides from `rounds.py` / `mc.json`, using the previous quiz's config as the template. Quiz #7's theme (green neon-brick) lives in the `THEME` dict plus a block at the end of `styles.css`: question slides stay black, while intro and reveal slides get `media/bg-green-brick.jpg`.

## Media Files

All media paths in JSON are relative to the root directory. Media files go in `media/` folder.

Video/audio autoplay only works after user interaction. `state.hasUserInteracted` is set to `true` on first click or keypress (app.js:121-122).

## Keyboard Controls

Global keyboard handler in `handleKeyPress()` (app.js:129-156):
- Arrow Right / Space → Next slide
- Arrow Left → Previous slide
- F → Toggle fullscreen
- S → Skip to countdown (question slides only)
- R → Restart timer (question slides only)

## Control Bar Behavior

Control bar (host-facing UI) is hidden by default, appears on mouse movement via `showControlBar()` (app.js:664-676). Auto-hides after 3 seconds of no mouse movement.

## When Modifying Slide Types

1. Add new type to switch in `renderCurrentSlide()` (app.js:209-242)
2. Create dedicated renderer function (e.g., `renderNewType()`)
3. Use helper functions: `createSlideContainer()`, `createElement()`, `createImage()`
4. Add CSS classes to `styles.css` with naming pattern: `.{type}-slide`
5. Update `quiz-config.example.json` with example
6. Document in README.md under "Slide Types"

## When Adding Features to Question Slides

If new feature applies to all question types:
1. Add to `isQuestionSlide()` helper (app.js:688-695)
2. Ensure `clearQuestionTimer()` is called on navigation
3. Test with S (skip) and R (restart) keyboard commands

## Styling Conventions

- All slides use flexbox centering (`.slide` class)
- Font sizes optimized for 16:9 projector viewing
- Timer uses `--accent-color` CSS variable (set from theme)
- Leaderboard top 3 get special background colors (styles.css:354-364)
- Media warnings use orange/amber color scheme (styles.css:377-384)

## Working with Keynote Exports

This project has a workflow for extracting quiz content from Keynote HTML exports:

### Keynote Export Structure

When Keynote exports to HTML, it creates:
- `index.html` - Main HTML file with JavaScript player
- `assets/header.json` - Contains `slideList` array with all slide UUIDs in order
- `assets/{UUID}/` - Individual slide folders with:
  - `{UUID}.json` - Slide metadata and layer information
  - `assets/{UUID}.pdf` - PDF textures for text/graphics rendering
  - `thumbnail.jpeg` - Preview thumbnail
  - Media files (videos, etc.) if present

### Extracting Quiz Content

Text content in Keynote exports is typically in two places:
1. **Accessibility array**: `slide.accessibility[]` contains text for screen readers
2. **PDF textures**: Visual text is rendered into PDFs and not easily extractable

**Important**: MCQ questions often show only 3 options in accessibility data while the 4th option (D) is embedded in PDF layers. When extracting:
- Use `"Not available"` as placeholder for missing 4th options
- Manual review and completion required
- Focus on extracting design patterns rather than complete content

### Generated Files from Extraction

After extracting from Keynote exports, you'll find:
- `quiz_complete_final.json` - Structured extraction data
- `quiz_full_content.txt` - Human-readable Q&A list
- `quiz_extraction_report.txt` - Slide-by-slide breakdown
- `EXTRACTION_SUMMARY.md` - Analysis report

These are reference files. The actual quiz runs from `quiz-config.json`.

### Keynote Design Patterns Identified

Common patterns from Keynote presentations:
- **Welcome slides**: Logo, title, subtitle, instructions
- **Prize slides**: Full-screen images showing prize information
- **Round intros**: Round number, subtitle (e.g., "multiple choice round"), instructions
- **Question number slides**: Transitional slides showing "Question X / Round Y"
- **MCQ questions**: Question text + 4 options + countdown video in corner
- **Free-text questions**: Question text + "Write the answer!" + points badge
- **Bonus questions**: Free-text with "2 points!" indicator
- **Break slides**: "BREAK TIME" or "We're about to resume!"
- **Answer slides**: Show all questions with correct answers highlighted
- **Thank you slides**: Closing slide with logo

### Media Asset Handling

Keynote exports duplicate media files across slide folders. When extracting:
- Countdown videos appear multiple times but are identical - copy only once
- Use the shortest path or first occurrence
- Rename to semantic names (e.g., `1130.mov` → `countdown.mov`)
- Logo and prize images may be embedded in PDFs - use thumbnails or manual export

### Creating New Quiz Configs from Keynote

When generating `quiz-config.json` from Keynote exports:
1. Preserve slide order from `header.json` slideList
2. Map Keynote slide types to app slide types (see "10 Slide Types" above)
3. Ensure all MCQ questions have exactly 4 options (use placeholders if needed)
4. Extract timer duration (typically 30 seconds) from video metadata
5. Link answer slides to questions via `questionRefId`
6. Mark incomplete data with `[To be filled]` for manual completion
