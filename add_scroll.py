import os

# Append CSS to styles.css
with open('/Users/ali/Documents/Academy/styles.css', 'a', encoding='utf-8') as f:
    f.write('''

/* ── SCROLL PROGRESS BAR ── */
.scroll-progress-container {
  position: absolute;
  bottom: -1px; /* Overlap border-bottom */
  left: 0;
  width: 100%;
  height: 4px;
  background: transparent;
  z-index: 1001;
}

.scroll-progress-bar {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, #FF9800, #FFC107);
  box-shadow: 0 0 10px rgba(255, 152, 0, 0.7);
  transition: width 0.1s ease-out;
  border-radius: 0 4px 4px 0;
}
''')

# Append JS to main.js
with open('/Users/ali/Documents/Academy/main.js', 'a', encoding='utf-8') as f:
    f.write('''

// ── Scroll Progress Bar ─────────────────────────────────────
(function initScrollProgress() {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;

  const container = document.createElement('div');
  container.className = 'scroll-progress-container';
  
  const bar = document.createElement('div');
  bar.className = 'scroll-progress-bar';
  bar.id = 'scroll-progress-bar';
  
  container.appendChild(bar);
  navbar.appendChild(container);

  window.addEventListener('scroll', () => {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    
    // Calculate percentage
    let scrolled = (winScroll / height) * 100;
    if (scrolled > 100) scrolled = 100;
    if (scrolled < 0) scrolled = 0;
    
    bar.style.width = scrolled + '%';
  });
})();
''')
