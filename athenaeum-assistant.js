/* ============================================================
   Athenaeum Assistant — Personal Teacher Assistant
   JavaScript Module v1.0
   
   Features:
   - Auth-aware: logged-in / free-trial / paid / guest
   - Gemini API integration (gemini-1.5-flash)
   - Bilingual auto-detection (English / Urdu / Roman Urdu)
   - Subject context (Math, Science, English, General)
   - Practice Quiz (MCQ, 5 questions, scoring, explanations)
   - Daily limits (5 questions / 2 quizzes for free-trial)
   - Student personalization (name from Supabase session)
============================================================ */

(function () {
  'use strict';

  /* ──────────────────────────────────────────────────────────
     CONFIGURATION — Vercel Serverless Endpoint
  ────────────────────────────────────────────────────────── */
  // The API key is now securely stored in Vercel Environment Variables.
  // We call our own secure backend instead of Google directly.
  const GEMINI_ENDPOINT = `/api/gemini`;

  /* ──────────────────────────────────────────────────────────
     LIMITS
  ────────────────────────────────────────────────────────── */
  const FREE_TRIAL_QUESTIONS_PER_DAY = 999999;
  const FREE_TRIAL_QUIZZES_PER_DAY   = 2;
  const PAID_LIMIT                   = Infinity;

  /* ──────────────────────────────────────────────────────────
     STATE
  ────────────────────────────────────────────────────────── */
  let state = {
    isLoggedIn:    false,
    isPaid:        false,
    userId:        null,
    studentName:   'Student',
    currentSubject:'general',
    chatHistory:   [],
    chatOpen:      false,
    quizOpen:      false,
    quizSubject:   null,
    quizData:      null,
    quizAnswers:   {},
    isTyping:      false,
    usageToday:    { questions: 0, quizzes: 0 }, // loaded from Supabase DB
  };

  /* ──────────────────────────────────────────────────────────
     TODAY KEY (localStorage daily reset — fallback only)
  ────────────────────────────────────────────────────────── */
  function todayKey() {
    return new Date().toISOString().split('T')[0]; // "2025-06-16"
  }

  function getUsageLocal(type) { // type: 'q' | 'quiz'
    if (!state.userId) return 0;
    const key = `ustad_${type}_${state.userId}_${todayKey()}`;
    return parseInt(localStorage.getItem(key) || '0', 10);
  }

  function incrementUsageLocal(type) {
    if (!state.userId) return;
    const key = `ustad_${type}_${state.userId}_${todayKey()}`;
    const cur = parseInt(localStorage.getItem(key) || '0', 10);
    localStorage.setItem(key, cur + 1);
  }

  // ── Supabase DB usage tracking ──────────────────────────
  async function getUsageFromDB() {
    try {
      const supabase = window.supabaseClient;
      if (!supabase || !state.userId) return { questions: 0, quizzes: 0 };
      const today = todayKey();
      const { data, error } = await supabase
        .from('ai_usage')
        .select('questions_used, quizzes_used')
        .eq('user_id', state.userId)
        .eq('usage_date', today)
        .maybeSingle();
      if (error || !data) return { questions: 0, quizzes: 0 };
      return { questions: data.questions_used, quizzes: data.quizzes_used };
    } catch { return { questions: 0, quizzes: 0 }; }
  }

  async function incrementUsageDB(type) { // type: 'questions' | 'quizzes'
    try {
      const supabase = window.supabaseClient;
      if (!supabase || !state.userId) return;
      const today = todayKey();
      const col = type === 'questions' ? 'questions_used' : 'quizzes_used';
      // Try to get existing record
      const { data } = await supabase
        .from('ai_usage')
        .select('id, ' + col)
        .eq('user_id', state.userId)
        .eq('usage_date', today)
        .maybeSingle();
      if (data) {
        await supabase.from('ai_usage')
          .update({ [col]: (data[col] || 0) + 1 })
          .eq('user_id', state.userId)
          .eq('usage_date', today);
      } else {
        await supabase.from('ai_usage')
          .insert({ user_id: state.userId, usage_date: today, [col]: 1 });
      }
    } catch (e) {
      // Fallback to localStorage if DB fails
      const localType = type === 'questions' ? 'q' : 'quiz';
      incrementUsageLocal(localType);
    }
  }

  function getRemainingQuestions() {
    if (state.isPaid) return PAID_LIMIT;
    return Math.max(0, FREE_TRIAL_QUESTIONS_PER_DAY - state.usageToday.questions);
  }

  function getRemainingQuizzes() {
    if (state.isPaid) return PAID_LIMIT;
    return Math.max(0, FREE_TRIAL_QUIZZES_PER_DAY - state.usageToday.quizzes);
  }

  /* ──────────────────────────────────────────────────────────
     SYSTEM PROMPT
  ────────────────────────────────────────────────────────── */
  function buildSystemPrompt(name, subject) {
    const subjectInstructions = {
      math: `- You are helping with Mathematics. ALWAYS show step-by-step solutions. Number each step clearly. Format math expressions clearly.`,
      science: `- You are helping with Science. Use simple, real-life examples to explain concepts. Make abstract ideas relatable.`,
      english: `- You are helping with English. Gently correct any grammar mistakes in the student's message. Never make them feel bad. Encourage improvement warmly.`,
      general: `- Help with any academic subject. Ask the student what subject they need help with if unclear.`,
    };

    const currentUrl = window.location.href;
    const currentTitle = document.title;
    
    let activeErrors = [];
    document.querySelectorAll('.error, .error-msg, .alert, [role="alert"]').forEach(el => {
      if(el.offsetParent !== null && el.innerText.trim()) {
        activeErrors.push(el.innerText.trim());
      }
    });
    const errorContext = activeErrors.length > 0 
      ? `\n\nVISIBLE ERRORS ON PAGE:\n- ${activeErrors.join('\n- ')}\nIf the student is confused about an error, refer to these.` 
      : '';

    return `You are Athenaeum Assistant, a personal AI teacher and website guide for students at Athenaeum Online Academy.

CURRENT PAGE CONTEXT (CRITICAL):
- The student is currently on page: ${currentUrl}
- Page Title: ${currentTitle}
- If the student says "I don't understand this" or asks a vague question, assume they are asking about the contents of this specific page.${errorContext}

PERSONA:
- Your name is "Athenaeum Assistant" — a warm, encouraging personal tutor and platform guide.
- The student's name is "${name}". Use it occasionally to make responses personal.

WEBSITE GUIDE (IMPORTANT):
- You must guide students on how to use the Athenaeum website.
- If they want to buy a course, tell them to click the "Enroll Now" button on the course cards which takes them to checkout.
- If they want a trial, tell them to click "Free Trial" to view live class timings.
- After they purchase a course, tell them it will appear in their Student Dashboard, where they can access Live Classes, Recordings, and Mock Exams.
- If they ask about quizzes or mock exams, tell them to go to their course dashboard after enrolling.
- You are friendly, patient, and genuinely care about the student's success.
- You speak like a caring teacher — supportive and motivating.
- The student's name is "${name}". Use it occasionally to make responses personal.

ACADEMICS & TECH SKILLS (IMPORTANT):
- Athenaeum Academy offers BOTH Academics (O/A Levels, Matric, Inter) AND Tech Skills & Bootcamps (Python Masterclass, Frontend Web Development with HTML/CSS/JS).
- If the student asks about coding, freelancing, earning money, or tech, you MUST smoothly pitch our Python and Web Development bootcamps. Explain how these high-income skills can secure their future, using your encouraging, premium tone.

LANGUAGE RULES (STRICTLY ENFORCED):
- You MUST ALWAYS respond in English ONLY.
- NEVER use Urdu, Hinglish, or Roman Urdu under any circumstances.
- If a student asks a question in Urdu or another language, reply to them in English and politely mention you only speak English.
- Your greeting is: "Hello ${name}! How can I help you today? 😊"

SUBJECT-SPECIFIC RULES:
${subjectInstructions[subject] || subjectInstructions.general}

FORMATTING:
- Keep responses concise but complete
- Use numbered steps for Math solutions
- Use bullet points for lists
- For code or formulas, keep them clear
- ALWAYS end every response with an encouraging line. Examples:
  * "Great question, ${name}! You are doing amazing! 🌟"
  * "Excellent work — you're getting better every day! 💪"
  * "Well done! Your hard work will pay off! 🏆"

BOUNDARIES:
- Only help with academic topics (Math, Science, English, etc.)
- If asked non-academic questions, gently redirect to studying
- Never be dismissive or harsh — always be encouraging`;
  }

  /* ──────────────────────────────────────────────────────────
     QUIZ PROMPT
  ────────────────────────────────────────────────────────── */
  function buildQuizPrompt(subject, topic, name) {
    const subjectMap = { math: 'Mathematics', science: 'Science', english: 'English' };
    const subjectLabel = subjectMap[subject] || subject;

    return `You are Athenaeum Assistant, a Pakistani academic tutor. Generate a practice quiz for a student named ${name}.

Subject: ${subjectLabel}
Topic: ${topic}

Create exactly 5 multiple choice questions. Return ONLY valid JSON in this exact format, no markdown, no explanation:

{
  "quiz_title": "Short descriptive title of quiz",
  "questions": [
    {
      "q": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": 0,
      "explanation": "Brief explanation of why this answer is correct"
    }
  ]
}

Rules:
- "answer" is the index (0-3) of the correct option in the options array
- Make questions appropriate for O-Level / Matric / FSc level
- Make explanations educational and encouraging
- Topic must be specifically about: ${topic}
- STRICT LANGUAGE RULE: ALL text (questions, options, explanations, titles) MUST be in English ONLY. No Urdu or Hinglish.
- Do not add any text before or after the JSON`;
  }

  /* ──────────────────────────────────────────────────────────
     GEMINI API CALL
  ────────────────────────────────────────────────────────── */
  async function callGemini(userMessage) {
    const systemPrompt = buildSystemPrompt(state.studentName, state.currentSubject);

    // Build contents array from history + new message
    const contents = [
      ...state.chatHistory,
      { role: 'user', parts: [{ text: userMessage }] }
    ];

    const requestBody = {
      system_instruction: { parts: [{ text: systemPrompt }] },
      contents: contents,
      generationConfig: {
        temperature: 0.7,
        topK: 40,
        topP: 0.95,
        maxOutputTokens: 1024,
      }
    };

    const response = await fetch(GEMINI_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      const errMsg = typeof errData.error === 'string' ? errData.error : errData.error?.message;
      throw new Error(errMsg || `API Error ${response.status}`);
    }

    const data = await response.json();
    const aiText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!aiText) throw new Error('Empty response from AI');

    // Update history
    state.chatHistory.push({ role: 'user',  parts: [{ text: userMessage }] });
    state.chatHistory.push({ role: 'model', parts: [{ text: aiText }] });

    // Keep history manageable (last 20 turns)
    if (state.chatHistory.length > 20) {
      state.chatHistory = state.chatHistory.slice(-20);
    }

    return aiText;
  }

  /* ──────────────────────────────────────────────────────────
     QUIZ GEMINI CALL
  ────────────────────────────────────────────────────────── */
  async function callGeminiQuiz(subject, topic) {
    const prompt = buildQuizPrompt(subject, topic, state.studentName);

    const requestBody = {
      contents: [{ role: 'user', parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: 0.4,
        topK: 40,
        topP: 0.95,
        maxOutputTokens: 2048,
      }
    };

    const response = await fetch(GEMINI_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      const errMsg = typeof errData.error === 'string' ? errData.error : errData.error?.message;
      throw new Error(errMsg || `API Error ${response.status}`);
    }

    const data = await response.json();
    let rawText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!rawText) throw new Error('Empty quiz response');

    // Strip markdown code blocks if present
    rawText = rawText.replace(/```json\s*/gi, '').replace(/```\s*/g, '').trim();

    return JSON.parse(rawText);
  }

  /* ──────────────────────────────────────────────────────────
     HTML BUILDER
  ────────────────────────────────────────────────────────── */
  function formatAIMessage(text) {
    // Escape HTML
    let safe = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Bold: **text**
    safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic: *text*
    safe = safe.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Numbered steps: detect lines starting with 1. 2. etc.
    const lines = safe.split('\n');
    let inList = false;
    let result = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const stepMatch = line.match(/^(\d+)\.\s+(.+)$/);

      if (stepMatch) {
        result.push(`<div class="step-block"><strong>Step ${stepMatch[1]}:</strong> ${stepMatch[2]}</div>`);
      } else if (line.match(/^[-•]\s+(.+)$/)) {
        result.push(`<div class="step-block">• ${line.replace(/^[-•]\s+/, '')}</div>`);
      } else if (line.trim() === '') {
        result.push('<br>');
      } else {
        // Check if it's the encouraging line (last line typically)
        const encouragePattern = /(Shabaash|Bohat acha|Excellent|Well done|You've got this|Hamesha|Keep it up|acha|great|amazing)/i;
        if (encouragePattern.test(line) && i >= lines.length - 2) {
          result.push(`<div class="encourage-line">${line}</div>`);
        } else {
          result.push(line);
        }
      }
    }

    return result.join('');
  }

  function getTimeStr() {
    return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  }

  /* ──────────────────────────────────────────────────────────
     DOM INJECTION — Main Widget HTML
  ────────────────────────────────────────────────────────── */
  function injectWidget() {
    // Wrapper
    const wrapper = document.createElement('div');
    wrapper.id = 'athenaeum-assistant-wrapper';

    // FAB button
    wrapper.innerHTML = `
      <div id="assistant-chat-panel">
        <!-- Header -->
        <div id="ustad-chat-header">
          <div class="athenaeum-assistant-avatar"><img src="logo_transparent.png" alt="Athenaeum"></div>
          <div class="ustad-header-info">
            <h4>Athenaeum Assistant</h4>
            <p><span class="ustad-online-dot"></span> Online · Your Personal Teacher</p>
          </div>
          <div class="ustad-header-actions">
            <button class="ustad-header-btn" id="ustad-clear-btn" title="Clear chat">🗑️</button>
            <button class="ustad-header-btn" id="ustad-minimize-btn" title="Minimize" style="font-size: 14px; margin-left: 6px; font-weight: bold; color: rgba(255,255,255,0.8);">✕</button>
          </div>
        </div>

        <!-- Trial Banner -->
        <div id="ustad-trial-banner" class="hidden">
          <span class="trial-text">⚡ <span id="ustad-q-remaining">5</span> questions remaining today</span>
          <a href="courses.html" class="trial-upgrade">Upgrade</a>
        </div>

        <!-- Subject Pills -->
        <div id="ustad-subject-pill">
          <button class="subject-tag general active" data-subject="general">📚 General</button>
          <button class="subject-tag math" data-subject="math">➕ Math</button>
          <button class="subject-tag science" data-subject="science">🔬 Science</button>
          <button class="subject-tag english" data-subject="english">📖 English</button>
        </div>

        <!-- Messages -->
        <div id="ustad-messages">
          <!-- Welcome card injected by JS -->
          <div id="ustad-typing" class="">
            <div class="ustad-msg-avatar"><img src="logo_transparent.png" alt="Athenaeum"></div>
            <div class="ustad-typing-bubble">
              <div class="ustad-typing-dot"></div>
              <div class="ustad-typing-dot"></div>
              <div class="ustad-typing-dot"></div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div id="ustad-input-area">
          <div id="ustad-input-row">
            <textarea
              id="ustad-text-input"
              placeholder="Ask me anything..."
              rows="1"
              maxlength="1000"
            ></textarea>
            <button class="ustad-quiz-btn" id="ustad-quiz-open-btn" title="Practice Quiz">
              📝 Quiz
            </button>
            <button class="ustad-send-btn" id="ustad-send-btn" title="Send message">
              <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </div>
          <p class="ustad-input-hint">Athenaeum Assistant · Powered by Google Gemini</p>
        </div>

        <p class="ustad-disclaimer">AI can make mistakes. Always verify important information.</p>
      </div>

      <button id="assistant-fab" class="${(window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/Academy/')) ? '' : 'round-fab'}" title="Open Athenaeum Assistant">
        <div class="teaser-icon"><img src="logo_transparent.png" alt="Athenaeum"></div>
        <div class="teaser-text">
          <strong>Athenaeum Assistant Personal Teacher</strong>
          <span>Welcome, <span id="ustad-user-name">Student</span>!</span>
        </div>
      </button>
    `;

    document.body.appendChild(wrapper);

    // Quiz Modal
    const quizModal = document.createElement('div');
    quizModal.id = 'ustad-quiz-modal';
    quizModal.innerHTML = `
      <div id="ustad-quiz-modal-backdrop"></div>
      <div id="ustad-quiz-card">
        <!-- Header -->
        <div class="quiz-modal-header">
          <h3>📝 Practice Quiz</h3>
          <button class="quiz-close-btn" id="ustad-quiz-close">✕</button>
        </div>

        <!-- Setup Screen -->
        <div id="ustad-quiz-setup">
          <div>
            <span class="quiz-setup-label">1. Select Subject</span>
            <div class="quiz-subject-grid">
              <div class="quiz-subject-option" data-subject="math">
                <span class="subj-emoji">➕</span>
                <span class="subj-name">Math</span>
              </div>
              <div class="quiz-subject-option" data-subject="science">
                <span class="subj-emoji">🔬</span>
                <span class="subj-name">Science</span>
              </div>
              <div class="quiz-subject-option" data-subject="english">
                <span class="subj-emoji">📖</span>
                <span class="subj-name">English</span>
              </div>
            </div>
          </div>
          <div>
            <span class="quiz-setup-label">2. Enter Topic <span style="font-weight:400;color:#94a3b8">(optional)</span></span>
            <input
              type="text"
              class="quiz-topic-input"
              id="ustad-quiz-topic"
              placeholder="e.g. Quadratic Equations, Photosynthesis, Tenses..."
              maxlength="80"
            >
          </div>
          <button class="quiz-start-btn" id="ustad-quiz-start-btn" disabled>
            🚀 Generate Quiz
          </button>
        </div>

        <!-- Loading Screen -->
        <div id="ustad-quiz-loading">
          <div class="quiz-loading-spinner"></div>
          <p class="quiz-loading-text">Athenaeum Assistant is preparing your quiz...<br>Thoda wait karein! 😊</p>
        </div>

        <!-- Questions Screen -->
        <div id="ustad-quiz-questions">
          <div class="quiz-progress-bar">
            <div class="quiz-progress-fill" id="ustad-quiz-progress" style="width:0%"></div>
          </div>
          <div class="quiz-questions-body" id="ustad-quiz-body"></div>
          <button class="quiz-submit-btn" id="ustad-quiz-submit-btn">
            ✅ Submit Answers
          </button>
        </div>

        <!-- Results Screen -->
        <div id="ustad-quiz-results">
          <div class="quiz-score-banner" id="ustad-quiz-score-banner">
            <div class="quiz-score-emoji" id="ustad-score-emoji">🎉</div>
            <div class="quiz-score-fraction" id="ustad-score-fraction">0/5</div>
            <div class="quiz-score-label">Questions Correct</div>
            <p class="quiz-encourage-msg" id="ustad-score-msg"></p>
          </div>
          <div class="quiz-results-body" id="ustad-quiz-results-body"></div>
          <div class="quiz-results-actions">
            <button class="quiz-retry-btn" id="ustad-quiz-retry-btn">🔄 Try Again</button>
            <button class="quiz-done-btn" id="ustad-quiz-done-btn">✅ Done</button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(quizModal);
  }

  /* ──────────────────────────────────────────────────────────
     DOM INJECTION — Teaser (for logged-out users)
  ────────────────────────────────────────────────────────── */
  function injectTeaser() {
    // Inject the teaser button
    const teaser = document.createElement('button');
    teaser.id = 'ustad-teaser-btn';
    teaser.style.border = 'none';
    teaser.style.cursor = 'pointer';
    const isIndex = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/Academy/');
    teaser.className = isIndex ? '' : 'round-fab';
    teaser.innerHTML = `
      <div class="teaser-icon">🔒</div>
      <div class="teaser-text" style="text-align: left;">
        <strong>Athenaeum Assistant Personal Teacher</strong>
        <span>Login to unlock your AI tutor</span>
      </div>
    `;
    
    // Inject the popup modal
    const popup = document.createElement('div');
    popup.id = 'ustad-teaser-popup';
    popup.style.display = 'none';
    popup.style.position = 'fixed';
    popup.style.bottom = '90px';
    popup.style.right = '20px';
    popup.style.width = '320px';
    popup.style.background = 'var(--card, #1e293b)';
    popup.style.border = '1px solid var(--border, #334155)';
    popup.style.borderRadius = '12px';
    popup.style.padding = '1.5rem';
    popup.style.boxShadow = '0 10px 25px rgba(0,0,0,0.5)';
    popup.style.zIndex = '10001';
    popup.style.textAlign = 'center';
    
    popup.innerHTML = `
      <button onclick="this.parentElement.style.display='none'" style="position:absolute; top:10px; right:10px; background:none; border:none; color:#94a3b8; cursor:pointer; font-size:16px;">✕</button>
      <div style="font-size:24px; margin-bottom:10px;">🔒</div>
      <p style="color: var(--text, #f8fafc); font-size: 0.95rem; line-height: 1.5; margin-bottom: 1rem;">
        Athenaeum Assistant is exclusively available for registered students!<br><br>
        Start your free trial today — it's completely free! <img src="logo_transparent.png" alt="Athenaeum" style="height:18px; vertical-align:middle;">
      </p>
      <div style="display:flex; flex-direction:column; gap:0.5rem;">
        <a href="auth.html?mode=register&ref=teaser" class="btn btn-primary" style="display:block; text-decoration:none; padding:0.5rem;">Start Free Trial</a>
        <a href="auth.html?mode=login&ref=teaser" class="btn btn-ghost" style="display:block; text-decoration:none; padding:0.5rem;">Login</a>
      </div>
    `;
    
    document.body.appendChild(popup);
    document.body.appendChild(teaser);
    
    teaser.addEventListener('click', () => {
      popup.style.display = popup.style.display === 'none' ? 'block' : 'none';
    });
  }

  /* ──────────────────────────────────────────────────────────
     WELCOME MESSAGE
  ────────────────────────────────────────────────────────── */
  function showWelcomeMessage(name) {
    const isIndex = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/Academy/');
    const messagesEl = document.getElementById('ustad-messages');
    const typing = document.getElementById('ustad-typing');

    const welcomeText = isIndex 
      ? `Hello <strong>${name}</strong>! 👋<br><br>I am your <strong>Athenaeum Assistant</strong> — your personal teacher. Ask me anything, I am here to help you learn and grow! 😊`
      : `Hello <strong>${name}</strong>! 👋<br><br>Need help about this page? I am your <strong>Athenaeum Assistant</strong>, here to help you on every page! 😊`;

    // Show typing indicator
    typing.classList.add('visible');
    
    setTimeout(() => {
      typing.classList.remove('visible');
      
      const msgEl = document.createElement('div');
      msgEl.classList.add('ustad-msg', 'ai-msg');
      msgEl.innerHTML = `
        <div class="ustad-msg-avatar"><img src="logo_transparent.png" alt="Athenaeum"></div>
        <div class="ustad-msg-content">
          <div class="ustad-msg-bubble" style="border-top-left-radius: 4px; border-bottom-left-radius: 20px;">${welcomeText}</div>
          <div class="ustad-msg-time">${getTimeStr()}</div>
        </div>
      `;

      const suggestionsEl = document.createElement('div');
      suggestionsEl.classList.add('ustad-suggestions');
      suggestionsEl.style.marginTop = '10px';
      suggestionsEl.style.marginBottom = '10px';
      suggestionsEl.innerHTML = `
          <button class="ustad-suggestion-chip" data-msg="Explain quadratic formula with steps">📐 Quadratic Formula</button>
          <button class="ustad-suggestion-chip" data-msg="What is photosynthesis? Give a simple example">🌿 Photosynthesis</button>
          <button class="ustad-suggestion-chip" data-msg="How to use past perfect tense with examples?">📝 Past Perfect</button>
          <button class="ustad-suggestion-chip" data-msg="Help me understand Newton's laws">🔬 Newton's Laws</button>
      `;

      messagesEl.insertBefore(msgEl, typing);
      messagesEl.insertBefore(suggestionsEl, typing);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }, 1500);
  }

  /* ──────────────────────────────────────────────────────────
     APPEND MESSAGE BUBBLE
  ────────────────────────────────────────────────────────── */
  function appendMessage(role, text, isFormatted = false) {
    const messagesEl = document.getElementById('ustad-messages');
    const typing = document.getElementById('ustad-typing');

    const msgEl = document.createElement('div');
    msgEl.classList.add('ustad-msg', role === 'user' ? 'user-msg' : 'ai-msg');

    const bubbleContent = isFormatted ? text : formatAIMessage(text);

    if (role === 'ai') {
      msgEl.innerHTML = `
        <div class="ustad-msg-avatar"><img src="logo_transparent.png" alt="Athenaeum"></div>
        <div class="ustad-msg-content">
          <div class="ustad-msg-bubble">${bubbleContent}</div>
          <div class="ustad-msg-time">${getTimeStr()}</div>
        </div>
      `;
    } else {
      msgEl.innerHTML = `
        <div class="ustad-msg-content">
          <div class="ustad-msg-bubble">${bubbleContent}</div>
          <div class="ustad-msg-time">${getTimeStr()}</div>
        </div>
      `;
    }

    messagesEl.insertBefore(msgEl, typing);
    
    // Auto-Scroll to Bottom
    setTimeout(() => {
      const chatBody = document.getElementById('ustad-messages');
      if (chatBody) {
        chatBody.scrollTop = chatBody.scrollHeight;
      }
    }, 50);
  }

  /* ──────────────────────────────────────────────────────────
     TRIAL BANNER UPDATE
  ────────────────────────────────────────────────────────── */
  function updateTrialBanner() {
    const banner = document.getElementById('ustad-trial-banner');
    if (banner) banner.style.display = 'none'; // Hide banner since it's unlimited now
  }

  /* ──────────────────────────────────────────────────────────
     SEND MESSAGE
  ────────────────────────────────────────────────────────── */
  async function sendMessage() {
    const input = document.getElementById('ustad-text-input');
    const sendBtn = document.getElementById('ustad-send-btn');
    const text = input.value.trim();
    if (!text || state.isTyping) return;

    // Check limit for free-trial users
    if (!state.isPaid && state.usageToday.questions >= FREE_TRIAL_QUESTIONS_PER_DAY) {
      showLimitReached('questions');
      return;
    }

    // Append user message
    appendMessage('user', escapeHtml(text), true);
    input.value = '';
    autoResizeTextarea(input);

    // Show typing
    state.isTyping = true;
    sendBtn.disabled = true;
    const typingEl = document.getElementById('ustad-typing');
    typingEl.classList.add('visible');

    const messagesEl = document.getElementById('ustad-messages');
    messagesEl.scrollTop = messagesEl.scrollHeight;

    try {
      const reply = await callGemini(text);
      typingEl.classList.remove('visible');
      appendMessage('ai', reply);

      // Increment usage in Supabase DB + local state
      if (!state.isPaid) {
        await incrementUsageDB('questions');
        state.usageToday.questions++;
        updateTrialBanner();
      }

    } catch (err) {
      typingEl.classList.remove('visible');
      console.error('Athenaeum Assistant error:', err);

      let errorMsg = 'I apologize! I am having trouble connecting to my AI core right now. Please try again in a moment. 🙏';

      if (err.message) {
        if (err.message.includes('API key') || err.message.includes('GEMINI_API_KEY')) {
          errorMsg = '⚠️ API key is not configured in Vercel. Please check environment variables.';
        } else if (err.message.includes('quota')) {
          errorMsg = '⚠️ API quota has been exceeded. Please try again later.';
        } else if (!err.message.includes('Unexpected token')) {
          errorMsg = `⚠️ Error: ${err.message}`;
        }
      }

      appendMessage('ai', errorMsg, true);
    } finally {
      state.isTyping = false;
      sendBtn.disabled = false;
    }
  }

  /* ──────────────────────────────────────────────────────────
     SHOW LIMIT REACHED
  ────────────────────────────────────────────────────────── */
  function showLimitReached(type) {
    const messagesEl = document.getElementById('ustad-messages');
    const typing = document.getElementById('ustad-typing');

    const existingLimit = messagesEl.querySelector('.ustad-limit-msg');
    if (existingLimit) existingLimit.remove();

    const limitEl = document.createElement('div');
    limitEl.classList.add('ustad-limit-msg');
    limitEl.style.textAlign = 'center';
    limitEl.style.border = '1px solid var(--border)';
    limitEl.style.padding = '1.5rem';
    limitEl.style.borderRadius = '12px';
    limitEl.style.margin = '1rem';

    if (type === 'questions') {
      limitEl.innerHTML = `
        <h4 style="margin-bottom: 0.5rem;">🔒 Daily Limit Reached!</h4>
        <p style="margin-bottom: 1.5rem; color: var(--muted); font-size: 0.9rem;">
          Your free trial allows ${FREE_TRIAL_QUESTIONS_PER_DAY} AI questions per day.<br><br>
          Purchase a course for unlimited access to Athenaeum Assistant, mock exams, and all lessons for that subject!
        </p>
        <a href="courses.html" class="btn btn-primary" style="display:block; margin-bottom: 0.5rem; text-decoration:none;">Browse Courses ✨</a>
        <button class="btn btn-ghost full-width" onclick="this.parentElement.remove()">Maybe Tomorrow</button>
      `;
    } else {
      limitEl.innerHTML = `
        <h4 style="margin-bottom: 0.5rem;">🔒 Quiz Limit Reached!</h4>
        <p style="margin-bottom: 1.5rem; color: var(--muted); font-size: 0.9rem;">
          Your free trial allows ${FREE_TRIAL_QUIZZES_PER_DAY} quizzes per day.<br><br>
          Purchase a course for unlimited practice!
        </p>
        <a href="courses.html" class="btn btn-primary" style="display:block; margin-bottom: 0.5rem; text-decoration:none;">Browse Courses ✨</a>
        <button class="btn btn-ghost full-width" onclick="this.parentElement.remove()">Maybe Tomorrow</button>
      `;
    }

    messagesEl.insertBefore(limitEl, typing);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  /* ──────────────────────────────────────────────────────────
     ESCAPE HTML
  ────────────────────────────────────────────────────────── */
  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;')
      .replace(/\n/g, '<br>');
  }

  /* ──────────────────────────────────────────────────────────
     AUTO-RESIZE TEXTAREA
  ────────────────────────────────────────────────────────── */
  function autoResizeTextarea(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 100) + 'px';
  }

  /* ──────────────────────────────────────────────────────────
     QUIZ FUNCTIONS
  ────────────────────────────────────────────────────────── */
  function openQuizModal() {
    if (!state.isPaid && getRemainingQuizzes() <= 0) {
      showLimitReached('quiz');
      return;
    }

    state.quizOpen = true;
    state.quizSubject = null;
    state.quizData = null;
    state.quizAnswers = {};

    // Reset to setup screen
    showQuizScreen('setup');
    document.getElementById('ustad-quiz-topic').value = '';
    document.querySelectorAll('.quiz-subject-option').forEach(el => el.classList.remove('selected'));
    document.getElementById('ustad-quiz-start-btn').disabled = true;

    document.getElementById('ustad-quiz-modal').classList.add('open');
  }

  function closeQuizModal() {
    state.quizOpen = false;
    document.getElementById('ustad-quiz-modal').classList.remove('open');
  }

  function showQuizScreen(screen) {
    ['setup', 'loading', 'questions', 'results'].forEach(s => {
      const el = document.getElementById(`ustad-quiz-${s}`);
      if (el) {
        if (s === screen) {
          el.classList.add('active');
        } else {
          el.classList.remove('active');
        }
      }
    });
  }

  async function startQuiz() {
    if (!state.quizSubject) return;

    const topic = document.getElementById('ustad-quiz-topic').value.trim() || state.quizSubject;
    showQuizScreen('loading');

    try {
      const quizData = await callGeminiQuiz(state.quizSubject, topic);
      state.quizData = quizData;
      state.quizAnswers = {};
      renderQuizQuestions(quizData);
      showQuizScreen('questions');

      // Increment quiz usage in DB + local state
      if (!state.isPaid) {
        await incrementUsageDB('quizzes');
        state.usageToday.quizzes++;
      }
    } catch (err) {
      console.error('Quiz generation error:', err);
      showQuizScreen('setup');
      alert('Quiz generate karne mein problem aayi. Please dobara try karein.');
    }
  }

  function renderQuizQuestions(quizData) {
    const body = document.getElementById('ustad-quiz-body');
    body.innerHTML = '';

    // Update progress to 0%
    document.getElementById('ustad-quiz-progress').style.width = '0%';

    quizData.questions.forEach((q, idx) => {
      const block = document.createElement('div');
      block.classList.add('quiz-question-block');
      block.innerHTML = `
        <div class="quiz-q-number">Question ${idx + 1} of ${quizData.questions.length}</div>
        <div class="quiz-q-text">${escapeHtml(q.q)}</div>
        <div class="quiz-options" id="quiz-options-${idx}">
          ${q.options.map((opt, optIdx) => `
            <label class="quiz-option-label" id="quiz-opt-${idx}-${optIdx}">
              <input type="radio" name="quiz-q-${idx}" value="${optIdx}">
              ${String.fromCharCode(65 + optIdx)}. ${escapeHtml(opt)}
            </label>
          `).join('')}
        </div>
      `;

      // Track answers
      block.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', () => {
          state.quizAnswers[idx] = parseInt(radio.value, 10);
          updateQuizProgress();
        });
      });

      body.appendChild(block);
    });
  }

  function updateQuizProgress() {
    const answered = Object.keys(state.quizAnswers).length;
    const total = state.quizData?.questions?.length || 5;
    const pct = (answered / total) * 100;
    document.getElementById('ustad-quiz-progress').style.width = pct + '%';
  }

  function submitQuiz() {
    if (!state.quizData) return;
    const questions = state.quizData.questions;
    const total = questions.length;

    // Check all answered
    if (Object.keys(state.quizAnswers).length < total) {
      alert('Please answer all questions before submitting! 📝');
      return;
    }

    let score = 0;
    questions.forEach((q, idx) => {
      if (state.quizAnswers[idx] === q.answer) score++;
    });

    // Show results
    showQuizResults(questions, score, total);
    showQuizScreen('results');
  }

  function showQuizResults(questions, score, total) {
    const emoji = score === total ? '🏆' : score >= total * 0.8 ? '🎉' : score >= total * 0.6 ? '😊' : score >= total * 0.4 ? '📚' : '💪';
    const encourageLines = {
      5: `Shabaash ${state.studentName}! Perfect score! Bohat acha! 🌟`,
      4: `Excellent ${state.studentName}! Almost perfect! Keep it up! 🎉`,
      3: `Good effort ${state.studentName}! Thodi aur practice karo! 💪`,
      2: `${state.studentName}, keep trying! Practice makes perfect! 📚`,
      1: `${state.studentName}, fikr mat karo! Revision karo aur dobara try karo! 🌟`,
      0: `${state.studentName}, revision ki zaroorat hai. Athenaeum Assistant se madad lo! 💪`,
    };

    document.getElementById('ustad-score-emoji').textContent = emoji;
    document.getElementById('ustad-score-fraction').textContent = `${score}/${total}`;
    document.getElementById('ustad-score-msg').textContent = encourageLines[score] || encourageLines[0];

    // Results body
    const body = document.getElementById('ustad-quiz-results-body');
    body.innerHTML = '';

    questions.forEach((q, idx) => {
      const userAnswer = state.quizAnswers[idx];
      const isCorrect = userAnswer === q.answer;
      const item = document.createElement('div');
      item.classList.add('quiz-result-item');
      item.innerHTML = `
        <div class="quiz-result-q">${idx + 1}. ${escapeHtml(q.q)}</div>
        ${!isCorrect ? `<div class="quiz-result-answer wrong">✗ Your answer: ${String.fromCharCode(65 + userAnswer)}. ${escapeHtml(q.options[userAnswer])}</div>` : ''}
        <div class="quiz-result-answer correct">✓ Correct: ${String.fromCharCode(65 + q.answer)}. ${escapeHtml(q.options[q.answer])}</div>
        <div class="quiz-result-explanation">💡 ${escapeHtml(q.explanation)}</div>
      `;
      body.appendChild(item);
    });
  }

  /* ──────────────────────────────────────────────────────────
     TOGGLE CHAT
  ────────────────────────────────────────────────────────── */
  function toggleChat() {
    state.chatOpen = !state.chatOpen;
    const panel = document.getElementById('assistant-chat-panel');
    const fab = document.getElementById('assistant-fab');

    if (state.chatOpen) {
      panel.classList.add('open');
      fab.classList.add('open');
      fab.title = 'Close Athenaeum Assistant';
      setTimeout(() => {
        const messagesEl = document.getElementById('ustad-messages');
        if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
        const input = document.getElementById('ustad-text-input');
        if (input) input.focus();
      }, 350);
    } else {
      panel.classList.remove('open');
      fab.classList.remove('open');
      fab.title = 'Open Athenaeum Assistant';
    }
  }

  /* ──────────────────────────────────────────────────────────
     BIND EVENTS
  ────────────────────────────────────────────────────────── */
  function bindEvents() {
    // FAB toggle
    const fab = document.getElementById('assistant-fab');
    if (fab) fab.addEventListener('click', toggleChat);

    // Minimize button toggle
    const minBtn = document.getElementById('ustad-minimize-btn');
    if (minBtn) minBtn.addEventListener('click', toggleChat);

    // Send button
    const sendBtn = document.getElementById('ustad-send-btn');
    if (sendBtn) sendBtn.addEventListener('click', sendMessage);

    // Textarea: Enter sends, Shift+Enter newline
    const input = document.getElementById('ustad-text-input');
    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      });
      input.addEventListener('input', () => autoResizeTextarea(input));
    }

    // Subject pills
    document.querySelectorAll('.subject-tag').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.subject-tag').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.currentSubject = btn.dataset.subject;
      });
    });

    // Suggestion chips
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('ustad-suggestion-chip')) {
        const msg = e.target.dataset.msg;
        const input = document.getElementById('ustad-text-input');
        if (input && msg) {
          input.value = msg;
          autoResizeTextarea(input);
          sendMessage();
        }
      }
    });

    // Clear chat
    const clearBtn = document.getElementById('ustad-clear-btn');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        if (confirm('Clear chat history? Sab messages delete ho jayenge.')) {
          state.chatHistory = [];
          const messagesEl = document.getElementById('ustad-messages');
          const typing = document.getElementById('ustad-typing');
          while (messagesEl.firstChild && messagesEl.firstChild !== typing) {
            messagesEl.removeChild(messagesEl.firstChild);
          }
          showWelcomeMessage(state.studentName);
        }
      });
    }

    // Quiz open button
    const quizOpenBtn = document.getElementById('ustad-quiz-open-btn');
    if (quizOpenBtn) quizOpenBtn.addEventListener('click', openQuizModal);

    // Quiz close
    const quizCloseBtn = document.getElementById('ustad-quiz-close');
    if (quizCloseBtn) quizCloseBtn.addEventListener('click', closeQuizModal);

    // Quiz backdrop click to close
    const quizBackdrop = document.getElementById('ustad-quiz-modal-backdrop');
    if (quizBackdrop) quizBackdrop.addEventListener('click', closeQuizModal);

    // Quiz subject selection
    document.querySelectorAll('.quiz-subject-option').forEach(opt => {
      opt.addEventListener('click', () => {
        document.querySelectorAll('.quiz-subject-option').forEach(o => o.classList.remove('selected'));
        opt.classList.add('selected');
        state.quizSubject = opt.dataset.subject;
        document.getElementById('ustad-quiz-start-btn').disabled = false;
      });
    });

    // Quiz start
    const quizStartBtn = document.getElementById('ustad-quiz-start-btn');
    if (quizStartBtn) quizStartBtn.addEventListener('click', startQuiz);

    // Quiz submit
    const quizSubmitBtn = document.getElementById('ustad-quiz-submit-btn');
    if (quizSubmitBtn) quizSubmitBtn.addEventListener('click', submitQuiz);

    // Quiz retry
    const quizRetryBtn = document.getElementById('ustad-quiz-retry-btn');
    if (quizRetryBtn) quizRetryBtn.addEventListener('click', () => {
      showQuizScreen('setup');
      document.querySelectorAll('.quiz-subject-option').forEach(el => el.classList.remove('selected'));
      state.quizSubject = null;
      state.quizData = null;
      state.quizAnswers = {};
      document.getElementById('ustad-quiz-start-btn').disabled = true;
      document.getElementById('ustad-quiz-topic').value = '';
    });

    // Quiz done
    const quizDoneBtn = document.getElementById('ustad-quiz-done-btn');
    if (quizDoneBtn) quizDoneBtn.addEventListener('click', closeQuizModal);

    // ESC key closes both
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (state.quizOpen) closeQuizModal();
        else if (state.chatOpen) toggleChat();
      }
    });
  }

  /* ──────────────────────────────────────────────────────────
     GET USER PLAN — reads from Supabase profiles table
  ────────────────────────────────────────────────────────── */
  async function getUserPlanFromDB(userId) {
    try {
      const supabase = window.supabaseClient;
      if (!supabase) return 'trial';
      const { data, error } = await supabase
        .from('profiles')
        .select('plan_type')
        .eq('id', userId)
        .maybeSingle();
      if (error || !data) return 'trial'; // default to trial if no profile yet
      return data.plan_type || 'trial';
    } catch {
      return 'trial'; // safe fallback
    }
  }

  /* ──────────────────────────────────────────────────────────
     MAIN INIT
  ────────────────────────────────────────────────────────── */
  async function init() {
    try {
      if (!window.supabaseClient) {
        injectTeaser();
        return;
      }

      const { data: { session }, error } = await window.supabaseClient.auth.getSession();

      if (!session || error) {
        injectTeaser();
        return;
      }

      const user = session.user;
      state.isLoggedIn = true;
      state.userId = user.id;

      // Get name from metadata
      const meta = user.user_metadata || {};
      const rawName = meta.full_name || meta.name || user.email?.split('@')[0] || 'Student';
      state.studentName = rawName.split(' ')[0] || rawName;

      // Get plan from Supabase profiles table (real DB, not metadata)
      const plan = await getUserPlanFromDB(user.id);
      state.isPaid = (plan === 'paid');

      // Load today's usage from DB
      state.usageToday = await getUsageFromDB();

      // Inject widget
      injectWidget();
      
      // Update name dynamically in the pill button
      const nameSpan = document.getElementById('ustad-user-name');
      if (nameSpan) {
        nameSpan.textContent = state.studentName;
      }

      bindEvents();
      updateTrialBanner();
      showWelcomeMessage(state.studentName);

      // Auth state change listener
      window.supabaseClient.auth.onAuthStateChange((event, newSession) => {
        if (event === 'SIGNED_OUT') {
          const wrapper = document.getElementById('athenaeum-assistant-wrapper');
          const modal = document.getElementById('ustad-quiz-modal');
          if (wrapper) wrapper.remove();
          if (modal) modal.remove();
          injectTeaser();
        }
      });

    } catch (err) {
      console.warn('Athenaeum Assistant init error:', err);
    }
  }

  /* ──────────────────────────────────────────────────────────
     BOOT
  ────────────────────────────────────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
