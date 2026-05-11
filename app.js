/**
 * Quiz Night Browser-Based Slideshow
 * Main application logic
 */

// ===== Application State =====
const state = {
    config: null,
    slides: [],
    currentSlideIndex: 0,
    currentQuestionTimer: null,
    currentQuestionTimerInterval: null,
    currentQuestionTimerAudio: null,
    countdownVideoElement: null,
    isCountdownPlaying: false,
    hasUserInteracted: false,
    controlBarTimeout: null,
    timerStarted: false
};

// ===== DOM Elements =====
const elements = {
    slideRoot: null,
    countdownOverlay: null,
    countdownVideo: null,
    controlBar: null,
    prevBtn: null,
    nextBtn: null,
    fullscreenBtn: null,
    slideCounter: null,
    errorDisplay: null
};

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', async () => {
    // Cache DOM elements
    elements.slideRoot = document.getElementById('slide-root');
    elements.countdownOverlay = document.getElementById('countdown-overlay');
    elements.countdownVideo = document.getElementById('countdown-video');
    elements.controlBar = document.getElementById('control-bar');
    elements.prevBtn = document.getElementById('prev-btn');
    elements.nextBtn = document.getElementById('next-btn');
    elements.fullscreenBtn = document.getElementById('fullscreen-btn');
    elements.slideCounter = document.getElementById('slide-counter');
    elements.errorDisplay = document.getElementById('error-display');

    // Set up event listeners
    setupEventListeners();

    // Load configuration
    await loadConfig();

    // Render first slide
    if (state.slides.length > 0) {
        renderCurrentSlide();
    }
});

// ===== Configuration Loading =====
async function loadConfig() {
    try {
        // Try to load quiz-config.json first
        let response = await fetch('quiz-config.json');

        if (!response.ok) {
            console.warn('quiz-config.json not found, falling back to example');
            response = await fetch('quiz-config.example.json');
        }

        if (!response.ok) {
            throw new Error('Could not load quiz configuration file');
        }

        state.config = await response.json();
        state.slides = state.config.slides || [];

        // Apply theme settings
        applyTheme();

        console.log(`Loaded ${state.slides.length} slides`);
    } catch (error) {
        showError(`Failed to load quiz configuration: ${error.message}`);
        console.error('Config loading error:', error);
    }
}

// ===== Theme Application =====
function applyTheme() {
    if (!state.config || !state.config.settings || !state.config.settings.theme) {
        return;
    }

    const theme = state.config.settings.theme;
    const root = document.documentElement;

    if (theme.backgroundColor) {
        document.body.style.backgroundColor = theme.backgroundColor;
    }
    if (theme.textColor) {
        document.body.style.color = theme.textColor;
    }
    if (theme.accentColor) {
        root.style.setProperty('--accent-color', theme.accentColor);
    }
    if (theme.secondaryAccent) {
        root.style.setProperty('--secondary-accent', theme.secondaryAccent);
    }
    if (theme.fontFamily) {
        document.body.style.fontFamily = theme.fontFamily;
    }
}

// ===== Event Listeners Setup =====
function setupEventListeners() {
    // Keyboard controls
    document.addEventListener('keydown', handleKeyPress);

    // Control bar buttons
    elements.prevBtn.addEventListener('click', goToPreviousSlide);
    elements.nextBtn.addEventListener('click', goToNextSlide);
    elements.fullscreenBtn.addEventListener('click', toggleFullscreen);

    // Mouse movement for control bar
    document.addEventListener('mousemove', showControlBar);

    // Track user interaction for autoplay compliance
    document.addEventListener('click', () => { state.hasUserInteracted = true; });
    document.addEventListener('keydown', () => { state.hasUserInteracted = true; });

    // Fullscreen change events
    document.addEventListener('fullscreenchange', updateFullscreenButton);
}

// ===== Keyboard Handler =====
function handleKeyPress(event) {
    const currentSlide = state.slides[state.currentSlideIndex];

    // If on a question slide and timer hasn't started, start it on any key press
    if (isQuestionSlide(currentSlide) && !state.timerStarted) {
        event.preventDefault();
        state.timerStarted = true;
        startQuestionTimer(currentSlide);
        return;
    }

    switch (event.key) {
        case 'ArrowRight':
        case ' ':
            event.preventDefault();
            goToNextSlide();
            break;
        case 'ArrowLeft':
            event.preventDefault();
            goToPreviousSlide();
            break;
        case 'f':
        case 'F':
            event.preventDefault();
            toggleFullscreen();
            break;
        case 's':
        case 'S':
            event.preventDefault();
            skipToCountdown();
            break;
        case 'r':
        case 'R':
            event.preventDefault();
            restartQuestionTimer();
            break;
    }
}

// ===== Navigation Functions =====
function goToNextSlide() {
    if (state.currentSlideIndex < state.slides.length - 1) {
        state.currentSlideIndex++;
        renderCurrentSlide();
    }
}

function goToPreviousSlide() {
    if (state.currentSlideIndex > 0) {
        state.currentSlideIndex--;
        renderCurrentSlide();
    }
}

function skipToCountdown() {
    const currentSlide = state.slides[state.currentSlideIndex];
    if (isQuestionSlide(currentSlide)) {
        clearQuestionTimer();
        showTimesUp();
    }
}

function restartQuestionTimer() {
    const currentSlide = state.slides[state.currentSlideIndex];
    if (isQuestionSlide(currentSlide) && !state.isCountdownPlaying) {
        clearQuestionTimer();
        state.timerStarted = true;
        startQuestionTimer(currentSlide);
    }
}

// ===== Slide Rendering =====
function renderCurrentSlide() {
    // Clear any existing timers and countdown
    clearQuestionTimer();
    hideCountdownVideo();

    // Reset timer started flag for new slide
    state.timerStarted = false;

    // Update slide counter
    updateSlideCounter();

    const slide = state.slides[state.currentSlideIndex];

    if (!slide) {
        showError('No slide to render');
        return;
    }

    // Hard-stop any media still attached from the previous slide
    // (innerHTML='' alone doesn't reliably stop playback — browsers keep
    // detached video/audio elements playing in the audio session until GC)
    stopAllMedia();

    // Clear existing content
    elements.slideRoot.innerHTML = '';

    // Render based on slide type
    switch (slide.type) {
        case 'welcome':
            renderWelcome(slide);
            break;
        case 'round-intro':
            renderRoundIntro(slide);
            break;
        case 'question-mcq':
            renderQuestionMcq(slide);
            break;
        case 'question-free-text':
            renderQuestionFreeText(slide);
            break;
        case 'question-video':
            renderQuestionVideo(slide);
            break;
        case 'question-audio':
            renderQuestionAudio(slide);
            break;
        case 'picture-question':
            renderPictureQuestion(slide);
            break;
        case 'picture-fullscreen':
            renderPictureFullscreen(slide);
            break;
        case 'picture-timer':
            renderPictureTimer(slide);
            break;
        case 'video-clip':
            renderVideoClip(slide);
            break;
        case 'video-fullscreen':
            renderVideoFullscreen(slide);
            break;
        case 'video-clip-timer':
            renderVideoClipTimer(slide);
            break;
        case 'answer':
            renderAnswer(slide);
            break;
        case 'leaderboard':
            renderLeaderboard(slide);
            break;
        case 'info':
            renderInfo(slide);
            break;
        case 'thank-you':
            renderThankYou(slide);
            break;
        default:
            showError(`Unknown slide type: ${slide.type}`);
    }
}

// ===== Slide Type Renderers =====

function renderWelcome(slide) {
    const container = createSlideContainer('welcome-slide');

    if (slide.logoImage) {
        const logo = createImage(slide.logoImage, 'logo-image');
        container.appendChild(logo);
    }

    if (slide.title) {
        const title = createElement('h1', 'slide-title', slide.title);
        container.appendChild(title);
    }

    if (slide.subtitle) {
        const subtitle = createElement('p', 'slide-subtitle', slide.subtitle);
        container.appendChild(subtitle);
    }

    elements.slideRoot.appendChild(container);
}

function renderRoundIntro(slide) {
    const container = createSlideContainer('round-intro-slide');

    if (slide.title) {
        const title = createElement('h1', 'slide-title', slide.title);
        container.appendChild(title);
    }

    if (slide.subtitle) {
        const subtitle = createElement('p', 'slide-subtitle', slide.subtitle);
        container.appendChild(subtitle);
    }

    if (slide.instructions) {
        const instructions = createElement('p', 'slide-instructions', slide.instructions);
        container.appendChild(instructions);
    }

    elements.slideRoot.appendChild(container);
}

function renderQuestionMcq(slide) {
    const container = createSlideContainer('question-slide question-mcq');

    // Question header (e.g., "Question 1")
    const header = createElement('div', 'question-header',
        `Question ${slide.questionNumber || ''}`);
    container.appendChild(header);

    // Question text
    const questionText = createElement('div', 'question-text', slide.questionText);
    container.appendChild(questionText);

    // Optional image
    if (slide.image) {
        const img = createImage(slide.image, 'question-image');
        container.appendChild(img);
    }

    // MCQ options
    const optionsContainer = createElement('div', 'mcq-options');
    const labels = ['A', 'B', 'C', 'D'];

    slide.options.forEach((option, index) => {
        const optionDiv = createElement('div', 'mcq-option');
        const label = createElement('span', 'mcq-option-label', labels[index]);
        const text = createElement('span', 'mcq-option-text', option);
        optionDiv.appendChild(label);
        optionDiv.appendChild(text);
        optionsContainer.appendChild(optionDiv);
    });

    container.appendChild(optionsContainer);
    elements.slideRoot.appendChild(container);

    // Timer will start on first key press (no auto-start)
}

function renderQuestionFreeText(slide) {
    const container = createSlideContainer('question-slide question-free-text');

    const header = createElement('div', 'question-header',
        `Question ${slide.questionNumber || ''}`);
    container.appendChild(header);

    const questionText = createElement('div', 'question-text', slide.questionText);
    container.appendChild(questionText);

    if (slide.image) {
        const img = createImage(slide.image, 'question-image');
        container.appendChild(img);
    }

    elements.slideRoot.appendChild(container);

    // Timer will start on first key press (no auto-start)
}

function renderQuestionVideo(slide) {
    const container = createSlideContainer('question-slide question-video');

    const header = createElement('div', 'question-header',
        `Question ${slide.questionNumber || ''}`);
    container.appendChild(header);

    const questionText = createElement('div', 'question-text', slide.questionText);
    container.appendChild(questionText);

    // Video element
    const video = document.createElement('video');
    video.className = 'question-video';
    video.controls = true;
    video.src = slide.videoSrc;

    if (slide.loop) {
        video.loop = true;
    }

    video.addEventListener('error', () => {
        const warning = createElement('div', 'media-warning',
            `Could not load video: ${slide.videoSrc}`);
        container.appendChild(warning);
    });

    // Autoplay if allowed and user has interacted
    if (slide.autoplay && state.hasUserInteracted) {
        video.play().catch(err => {
            console.warn('Autoplay failed:', err);
        });
    }

    container.appendChild(video);
    elements.slideRoot.appendChild(container);

    // Timer will start on first key press (no auto-start)
}

function renderQuestionAudio(slide) {
    const container = createSlideContainer('question-slide question-audio');

    const header = createElement('div', 'question-header',
        `Question ${slide.questionNumber || ''}`);
    container.appendChild(header);

    const questionText = createElement('div', 'question-text', slide.questionText);
    container.appendChild(questionText);

    // Show subtitle if provided
    if (slide.subtitle) {
        const subtitle = createElement('div', 'question-subtitle', slide.subtitle);
        container.appendChild(subtitle);
    }

    // Audio element
    if (slide.audioSrc) {
        const audio = document.createElement('audio');
        audio.className = 'question-audio';
        audio.controls = true;
        audio.src = slide.audioSrc;

        if (slide.loop) {
            audio.loop = true;
        }

        audio.addEventListener('error', () => {
            const warning = createElement('div', 'media-warning',
                `Could not load audio: ${slide.audioSrc}`);
            container.appendChild(warning);
        });

        if (state.hasUserInteracted) {
            audio.play().catch(err => {
                console.warn('Autoplay failed:', err);
            });
        }

        container.appendChild(audio);
    }

    elements.slideRoot.appendChild(container);

    // Timer will start on first key press (no auto-start)
}

function renderAnswer(slide) {
    const container = createSlideContainer('answer-slide');

    // Find the referenced question slide
    const questionSlide = state.slides.find(s => s.id === slide.questionRefId);

    if (!questionSlide) {
        const warning = createElement('div', 'media-warning',
            `Warning: Could not find question with ID: ${slide.questionRefId}`);
        container.appendChild(warning);
        elements.slideRoot.appendChild(container);
        return;
    }

    // Show question number header
    if (questionSlide.questionNumber) {
        const header = createElement('div', 'question-header',
            `Question ${questionSlide.questionNumber}`);
        container.appendChild(header);
    }

    // Show answer title
    if (slide.title) {
        const title = createElement('h2', 'slide-title', slide.title);
        container.appendChild(title);
    }

    // Show original question text
    const questionText = createElement('div', 'question-text', questionSlide.questionText);
    container.appendChild(questionText);

    // For MCQ, show options with correct one highlighted
    if (questionSlide.type === 'question-mcq') {
        const optionsContainer = createElement('div', 'mcq-options');
        const labels = ['A', 'B', 'C', 'D'];

        questionSlide.options.forEach((option, index) => {
            const optionDiv = createElement('div', 'mcq-option');
            if (index === questionSlide.correctOptionIndex) {
                optionDiv.classList.add('correct');
            }
            const label = createElement('span', 'mcq-option-label', labels[index]);
            const text = createElement('span', 'mcq-option-text', option);
            optionDiv.appendChild(label);
            optionDiv.appendChild(text);
            optionsContainer.appendChild(optionDiv);
        });

        container.appendChild(optionsContainer);
    } else {
        // For free-text/video/audio questions, show correct answer text
        if (questionSlide.correctAnswerText) {
            const answerText = createElement('div', 'answer-text', questionSlide.correctAnswerText);
            container.appendChild(answerText);
        }
    }

    // Show extra text if provided
    if (slide.extraText) {
        const extraText = createElement('div', 'answer-extra-text', slide.extraText);
        container.appendChild(extraText);
    }

    elements.slideRoot.appendChild(container);
}

function renderLeaderboard(slide) {
    const container = createSlideContainer('leaderboard-container');

    if (slide.title) {
        const title = createElement('h1', 'leaderboard-title', slide.title);
        container.appendChild(title);
    }

    // Sort teams by score descending
    const sortedTeams = [...slide.teams].sort((a, b) => b.score - a.score);

    // Create table
    const table = document.createElement('table');
    table.className = 'leaderboard-table';

    // Table header
    const thead = document.createElement('thead');
    thead.innerHTML = `
        <tr>
            <th>Rank</th>
            <th>Team</th>
            <th>Score</th>
        </tr>
    `;
    table.appendChild(thead);

    // Table body
    const tbody = document.createElement('tbody');
    sortedTeams.forEach((team, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="leaderboard-rank">${index + 1}</td>
            <td class="leaderboard-name">${team.name}</td>
            <td class="leaderboard-score">${team.score}</td>
        `;
        tbody.appendChild(row);
    });
    table.appendChild(tbody);

    container.appendChild(table);
    elements.slideRoot.appendChild(container);
}

function renderInfo(slide) {
    const container = createSlideContainer('info-slide');

    if (slide.title) {
        const title = createElement('h1', 'slide-title', slide.title);
        container.appendChild(title);
    }

    if (slide.subtitle) {
        const subtitle = createElement('p', 'slide-subtitle', slide.subtitle);
        container.appendChild(subtitle);
    }

    if (slide.htmlContent) {
        const htmlDiv = document.createElement('div');
        htmlDiv.className = 'slide-html-content';
        htmlDiv.innerHTML = slide.htmlContent;
        container.appendChild(htmlDiv);
    }

    if (slide.image) {
        const img = createImage(slide.image, 'slide-image');
        if (slide.fullscreenImage) {
            img.classList.add('fullscreen');
        }
        container.appendChild(img);
    }

    elements.slideRoot.appendChild(container);
}

function renderThankYou(slide) {
    const container = createSlideContainer('thank-you-slide');

    if (slide.title) {
        const title = createElement('h1', 'slide-title', slide.title);
        container.appendChild(title);
    }

    if (slide.subtitle) {
        const subtitle = createElement('p', 'slide-subtitle', slide.subtitle);
        container.appendChild(subtitle);
    }

    elements.slideRoot.appendChild(container);
}

function renderPictureQuestion(slide) {
    const container = createSlideContainer('picture-question-slide');

    if (slide.questionNumber) {
        const header = createElement('div', 'question-header',
            `Question ${slide.questionNumber}`);
        container.appendChild(header);
    }

    const questionText = createElement('div', 'video-clip-question',
        slide.questionText || 'Identify what you see in the picture');
    container.appendChild(questionText);

    if (slide.instructions) {
        const instructions = createElement('p', 'slide-instructions', slide.instructions);
        container.appendChild(instructions);
    }

    elements.slideRoot.appendChild(container);
}

function renderPictureFullscreen(slide) {
    const container = createSlideContainer('picture-fullscreen-slide');

    const img = document.createElement('img');
    img.className = 'fullscreen-picture';
    img.src = slide.image;
    img.alt = slide.altText || 'Quiz picture';

    img.addEventListener('error', () => {
        const warning = createElement('div', 'media-warning',
            `Could not load image: ${slide.image}`);
        container.appendChild(warning);
    });

    container.appendChild(img);
    elements.slideRoot.appendChild(container);
}

function renderPictureTimer(slide) {
    const container = createSlideContainer('picture-timer-slide');

    // Image takes up most of the space
    if (slide.image) {
        const img = document.createElement('img');
        img.className = 'picture-timer-image';
        img.src = slide.image;
        img.alt = slide.altText || 'Quiz picture';
        img.addEventListener('error', () => {
            const warning = createElement('div', 'media-warning',
                `Could not load image: ${slide.image}`);
            container.appendChild(warning);
        });
        container.appendChild(img);
    }

    // Question text overlay at the bottom
    const overlay = createElement('div', 'picture-timer-overlay', '');
    if (slide.questionNumber) {
        const header = createElement('span', 'picture-timer-header',
            `Q${slide.questionNumber}: `);
        overlay.appendChild(header);
    }
    const questionText = document.createElement('span');
    questionText.innerHTML = slide.questionText || 'Identify what you see in the picture';
    overlay.appendChild(questionText);
    container.appendChild(overlay);

    elements.slideRoot.appendChild(container);
}

function renderVideoClip(slide) {
    const container = createSlideContainer('video-clip-slide');

    // Question header (e.g., "Question 1")
    if (slide.questionNumber) {
        const header = createElement('div', 'question-header',
            `Question ${slide.questionNumber}`);
        container.appendChild(header);
    }

    // Question text
    const questionText = createElement('div', 'video-clip-question',
        slide.questionText || 'Name the TV/Movie from the clip');
    container.appendChild(questionText);

    // Instructions
    if (slide.instructions) {
        const instructions = createElement('p', 'slide-instructions', slide.instructions);
        container.appendChild(instructions);
    }

    elements.slideRoot.appendChild(container);
}

function renderVideoFullscreen(slide) {
    const container = createSlideContainer('video-fullscreen-slide');

    // Video element
    const video = document.createElement('video');
    video.className = 'fullscreen-video';
    video.controls = true;
    video.src = slide.videoSrc;

    if (slide.loop) {
        video.loop = true;
    }

    video.addEventListener('error', () => {
        const warning = createElement('div', 'media-warning',
            `Could not load video: ${slide.videoSrc}`);
        container.appendChild(warning);
    });

    // Autoplay if allowed and user has interacted
    if (state.hasUserInteracted) {
        video.play().catch(err => {
            console.warn('Autoplay failed:', err);
        });
    }

    container.appendChild(video);
    elements.slideRoot.appendChild(container);
}

function renderVideoClipTimer(slide) {
    const container = createSlideContainer('video-clip-timer-slide');

    // Question header (e.g., "Question 1")
    if (slide.questionNumber) {
        const header = createElement('div', 'question-header',
            `Question ${slide.questionNumber}`);
        container.appendChild(header);
    }

    // Question text
    const questionText = createElement('div', 'video-clip-question',
        slide.questionText || 'Name the TV/Movie from the clip');
    container.appendChild(questionText);

    // Instructions
    if (slide.instructions) {
        const instructions = createElement('p', 'slide-instructions', slide.instructions);
        container.appendChild(instructions);
    }

    elements.slideRoot.appendChild(container);

    // Timer will start on first key press (no auto-start)
}

// ===== Question Timer Logic =====

function startQuestionTimer(slide) {
    // Determine timer duration
    const duration = slide.timerSeconds ||
                    (state.config.settings && state.config.settings.defaultQuestionDurationSec) ||
                    30;

    // Create timer display
    const timerDisplay = createElement('div', 'question-timer', duration.toString());
    elements.slideRoot.appendChild(timerDisplay);

    // Create countdown audio element
    const countdownAudio = new Audio();
    const audioSrc = (state.config.settings && state.config.settings.countdownAudio)
        || 'media/countdown.mp3';
    countdownAudio.src = audioSrc;
    countdownAudio.volume = 0.5;

    // Start playing audio immediately if user has interacted
    if (state.hasUserInteracted) {
        countdownAudio.play().catch(err => {
            console.warn('Could not play countdown audio:', err);
        });
    }

    let remainingTime = duration;

    // Update timer every second
    const intervalId = setInterval(() => {
        remainingTime--;
        timerDisplay.textContent = remainingTime;

        if (remainingTime <= 0) {
            clearInterval(intervalId);
        }
    }, 1000);

    // Store audio reference and interval for cleanup
    state.currentQuestionTimerAudio = countdownAudio;
    state.currentQuestionTimerInterval = intervalId;

    // Set timeout for full duration
    state.currentQuestionTimer = setTimeout(() => {
        clearInterval(intervalId);
        showTimesUp();
    }, duration * 1000);
}

function clearQuestionTimer() {
    if (state.currentQuestionTimer) {
        clearTimeout(state.currentQuestionTimer);
        state.currentQuestionTimer = null;
    }

    if (state.currentQuestionTimerInterval) {
        clearInterval(state.currentQuestionTimerInterval);
        state.currentQuestionTimerInterval = null;
    }

    if (state.currentQuestionTimerAudio) {
        state.currentQuestionTimerAudio.pause();
        state.currentQuestionTimerAudio.currentTime = 0;
        state.currentQuestionTimerAudio = null;
    }
}

function showTimesUp() {
    // Hide all answer options
    const optionsContainer = document.querySelector('.mcq-options');
    const freeTextPrompt = document.querySelector('.free-text-prompt');

    if (optionsContainer) {
        optionsContainer.style.display = 'none';
    }
    if (freeTextPrompt) {
        freeTextPrompt.style.display = 'none';
    }

    // Create and show "TIME'S UP!" message
    const timesUpDiv = createElement('div', 'times-up-message', "TIME'S UP!");
    elements.slideRoot.appendChild(timesUpDiv);

    // No auto-advance - user must manually advance to next slide
}

// ===== Countdown Video Logic =====

function startCountdownVideoThenAdvance() {
    if (!state.config || !state.config.settings || !state.config.settings.countdownVideo) {
        console.warn('No countdown video configured, advancing immediately');
        goToNextSlide();
        return;
    }

    state.isCountdownPlaying = true;

    // Set video source
    elements.countdownVideo.src = state.config.settings.countdownVideo;

    // Show overlay
    elements.countdownOverlay.classList.remove('hidden');

    // Handle video end
    elements.countdownVideo.onended = () => {
        hideCountdownVideo();
        goToNextSlide();
    };

    // Handle video error
    elements.countdownVideo.onerror = () => {
        console.error('Countdown video failed to load');
        hideCountdownVideo();
        goToNextSlide();
    };

    // Play video
    elements.countdownVideo.play().catch(err => {
        console.error('Failed to play countdown video:', err);
        hideCountdownVideo();
        goToNextSlide();
    });
}

function hideCountdownVideo() {
    state.isCountdownPlaying = false;
    elements.countdownOverlay.classList.add('hidden');
    elements.countdownVideo.pause();
    elements.countdownVideo.src = '';
}

// ===== Fullscreen Controls =====

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
            console.error('Error entering fullscreen:', err);
        });
    } else {
        document.exitFullscreen();
    }
}

function updateFullscreenButton() {
    if (document.fullscreenElement) {
        elements.fullscreenBtn.textContent = '⤢ Exit Fullscreen';
    } else {
        elements.fullscreenBtn.textContent = '⤢ Fullscreen';
    }
}

// ===== Control Bar Visibility =====

function showControlBar() {
    elements.controlBar.classList.add('visible');

    // Clear existing timeout
    if (state.controlBarTimeout) {
        clearTimeout(state.controlBarTimeout);
    }

    // Hide after 3 seconds of no movement
    state.controlBarTimeout = setTimeout(() => {
        elements.controlBar.classList.remove('visible');
    }, 3000);
}

// ===== UI Updates =====

function updateSlideCounter() {
    const current = state.currentSlideIndex + 1;
    const total = state.slides.length;
    elements.slideCounter.textContent = `Slide ${current} / ${total}`;
}

// ===== Utility Functions =====

function isQuestionSlide(slide) {
    return slide && (
        slide.type === 'question-mcq' ||
        slide.type === 'question-free-text' ||
        slide.type === 'question-video' ||
        slide.type === 'question-audio' ||
        slide.type === 'video-clip-timer' ||
        slide.type === 'picture-timer'
    );
}

function createSlideContainer(className) {
    const container = document.createElement('div');
    container.className = `slide ${className}`;
    return container;
}

function stopAllMedia() {
    // Pause every video/audio in the slide root and unload its source.
    // load() after clearing src forces the buffer to discard, which stops
    // any audio session that would otherwise persist past detachment.
    const media = elements.slideRoot.querySelectorAll('video, audio');
    media.forEach(m => {
        try {
            m.pause();
            m.removeAttribute('src');
            m.load();
        } catch (e) {
            // best-effort; ignore
        }
    });
}

function createElement(tag, className, textContent = '') {
    const element = document.createElement(tag);
    element.className = className;
    if (textContent) {
        element.innerHTML = textContent;
    }
    return element;
}

function createImage(src, className) {
    const img = document.createElement('img');
    img.className = className;
    img.src = src;
    img.addEventListener('error', () => {
        img.style.display = 'none';
        const warning = createElement('div', 'media-warning',
            `Could not load image: ${src}`);
        img.parentElement.appendChild(warning);
    });
    return img;
}

function showError(message) {
    elements.errorDisplay.textContent = message;
    elements.errorDisplay.classList.remove('hidden');
}

function hideError() {
    elements.errorDisplay.classList.add('hidden');
}
