import re

# 1. Update HTML
with open('/Users/ali/Documents/Academy/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html_start_marker = '<!-- Carousel wrapper -->'
html_end_marker = '<!-- /Student Achievements -->'

html_start_idx = html.find(html_start_marker)

# We need to find where the old carousel ends
old_carousel_end = html.find('</div><!-- /.carousel -->')
old_controls_end = html.find('</div>\n    </section>', old_carousel_end)

if html_start_idx != -1 and old_controls_end != -1:
    new_html = """<!-- Orbit Testimonial System -->
        <div class="orbit-container" id="orbit-system">
          
          <!-- Left: Rotating Circle -->
          <div class="orbit-left">
            <div class="orbit-ring" id="orbit-ring">
              <!-- Avatars -->
              <div class="orbit-avatar-wrapper" data-index="0" style="--angle: 0deg;">
                <div class="orbit-avatar active" style="background: linear-gradient(135deg,#005088,#11CAA0);">FA</div>
              </div>
              <div class="orbit-avatar-wrapper" data-index="1" style="--angle: 60deg;">
                <div class="orbit-avatar" style="background: linear-gradient(135deg,#11CAA0,#005088);">AR</div>
              </div>
              <div class="orbit-avatar-wrapper" data-index="2" style="--angle: 120deg;">
                <div class="orbit-avatar" style="background: linear-gradient(135deg,#FFD700,#005088);">ZK</div>
              </div>
              <div class="orbit-avatar-wrapper" data-index="3" style="--angle: 180deg;">
                <div class="orbit-avatar" style="background: linear-gradient(135deg,#005088,#FFD700);">HS</div>
              </div>
              <div class="orbit-avatar-wrapper" data-index="4" style="--angle: 240deg;">
                <div class="orbit-avatar" style="background: linear-gradient(135deg,#11CAA0,#FFD700);">NM</div>
              </div>
              <div class="orbit-avatar-wrapper" data-index="5" style="--angle: 300deg;">
                <div class="orbit-avatar" style="background: linear-gradient(135deg,#005088,#11CAA0);">UI</div>
              </div>
            </div>
          </div>

          <!-- Right: Text Content -->
          <div class="orbit-right">
            <div class="testimonial-display" id="testimonial-display">
              <span class="orbit-quote-mark">&ldquo;</span>
              
              <div class="orbit-badge" id="orb-badge">A*</div>
              
              <p class="orbit-quote-text" id="orb-quote">
                Athenaeum transformed my O-Level preparation completely. The structured lessons and past-paper practice gave me the confidence I needed. I achieved A* in Biology!
              </p>
              
              <div class="orbit-author">
                <h4 id="orb-name">Fatima Anwar</h4>
                <p id="orb-detail">O-Level Biology &bull; Cambridge Board</p>
              </div>
              
              <div class="orbit-results">
                <span class="result-pill pill--astar" id="orb-pill1">A* Grade</span>
                <span class="result-pill pill--subject" id="orb-pill2">Biology</span>
              </div>
            </div>
          </div>

        </div>
"""
    # Replace from html_start_marker to the end of the carousel controls
    html = html[:html_start_idx] + new_html + html[old_controls_end:]
    with open('/Users/ali/Documents/Academy/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("HTML updated.")


# 2. Update CSS
with open('/Users/ali/Documents/Academy/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

css_start_marker = "/* ── 17. SUCCESS STORIES CAROUSEL ────────────────────────── */"
css_end_marker = "/* Grade summary bar */"
css_start_idx = css.find(css_start_marker)
css_end_idx = css.find(css_end_marker)

if css_start_idx != -1 and css_end_idx != -1:
    new_css = """/* ── 17. SUCCESS STORIES ORBIT ────────────────────────── */
.stories {
  background: linear-gradient(180deg, var(--clr-white) 0%, var(--clr-surface-alt) 100%);
  padding: 80px 0;
  overflow: hidden;
}

.orbit-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 60px;
  max-width: 1100px;
  margin: 60px auto 0;
}

/* Left Side: Orbit Ring */
.orbit-left {
  flex: 0 0 45%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.orbit-ring {
  width: 380px;
  height: 380px;
  border-radius: 50%;
  border: 2px dashed rgba(0, 80, 136, 0.2);
  position: relative;
  transition: transform 0.8s cubic-bezier(0.25, 1, 0.5, 1);
  will-change: transform;
}

.orbit-ring::after {
  content: '';
  position: absolute;
  top: 50%; left: 50%;
  width: 120px; height: 120px;
  background: radial-gradient(circle, rgba(0,210,255,0.15) 0%, rgba(0,80,136,0) 70%);
  transform: translate(-50%, -50%);
  border-radius: 50%;
  pointer-events: none;
}

.orbit-avatar-wrapper {
  position: absolute;
  top: 50%; left: 50%;
  width: 64px; height: 64px;
  margin: -32px 0 0 -32px;
  transform: rotate(var(--angle)) translateY(-190px);
}

.orbit-avatar {
  width: 100%; height: 100%;
  border-radius: 50%;
  display: grid; place-items: center;
  color: #fff; font-weight: 800; font-size: 18px;
  border: 4px solid var(--clr-white);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease, filter 0.3s ease;
  transform: rotate(calc(-1 * var(--current-ring-rotation, 0deg) - var(--angle)));
  filter: grayscale(80%) opacity(0.6);
}

.orbit-avatar:hover {
  transform: rotate(calc(-1 * var(--current-ring-rotation, 0deg) - var(--angle))) scale(1.1);
}

.orbit-avatar.active {
  filter: grayscale(0%) opacity(1);
  box-shadow: 0 0 0 6px rgba(0, 210, 255, 0.3);
  transform: rotate(calc(-1 * var(--current-ring-rotation, 0deg) - var(--angle))) scale(1.2);
}

/* Right Side: Text Display */
.orbit-right {
  flex: 0 0 50%;
  position: relative;
}

.testimonial-display {
  background: var(--clr-white);
  padding: 50px 40px;
  border-radius: var(--radius-xl);
  box-shadow: 0 20px 48px rgba(0, 80, 136, 0.08);
  position: relative;
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.testimonial-display.fade-out {
  opacity: 0;
  transform: translateX(15px);
}

.orbit-quote-mark {
  position: absolute;
  top: -15px; left: -10px;
  font-family: var(--font-heading);
  font-size: 10rem;
  line-height: 1;
  color: rgba(0, 210, 255, 0.05);
  z-index: 0;
  pointer-events: none;
}

.orbit-badge {
  position: absolute;
  top: 30px; right: 30px;
  padding: 6px 16px;
  border-radius: 20px;
  font-family: var(--font-heading);
  font-size: 14px; font-weight: 800;
  background: linear-gradient(135deg, #FF9800, #FF5722);
  color: #fff;
  box-shadow: 0 4px 12px rgba(255, 152, 0, .3);
  z-index: 2;
}

.orbit-quote-text {
  font-size: 18px;
  color: var(--clr-on-surface);
  line-height: 1.8;
  margin-bottom: 30px;
  font-weight: 500;
  position: relative; z-index: 2;
}

.orbit-author {
  border-top: 1px solid var(--clr-surface-high);
  padding-top: 20px;
  margin-bottom: 20px;
  position: relative; z-index: 2;
}

.orbit-author h4 {
  font-family: var(--font-heading);
  font-size: 20px;
  color: var(--clr-on-surface);
}

.orbit-author p {
  font-size: 14px;
  color: var(--clr-on-surface-var);
  margin-top: 5px;
}

.orbit-results {
  display: flex; gap: 10px; flex-wrap: wrap; position: relative; z-index: 2;
}

.result-pill {
  padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700;
}

.pill--astar { background: rgba(255, 152, 0, 0.1); color: #E65100; }
.pill--a { background: rgba(0, 210, 255, 0.1); color: #0077b6; }
.pill--subject { background: rgba(123, 44, 191, 0.08); color: var(--clr-purple); }

@media (max-width: 992px) {
  .orbit-container {
    flex-direction: column;
    gap: 60px;
  }
  .orbit-ring {
    width: 280px; height: 280px;
  }
  .orbit-avatar-wrapper {
    transform: rotate(var(--angle)) translateY(-140px);
  }
}

"""
    css = css[:css_start_idx] + new_css + css[css_end_idx:]
    with open('/Users/ali/Documents/Academy/styles.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("CSS updated.")


# 3. Update JS
with open('/Users/ali/Documents/Academy/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

js_start_marker = "// ── Success Stories Carousel ────────────────────────────────"
js_end_marker = "// ── WhatsApp Floating Widget ────────────────────────────────"

js_start_idx = js.find(js_start_marker)
js_end_idx = js.find(js_end_marker)

if js_start_idx != -1 and js_end_idx != -1:
    new_js = """// ── Orbit Testimonial System ────────────────────────────────
(function initOrbitCarousel() {
  const ring = document.getElementById('orbit-ring');
  const display = document.getElementById('testimonial-display');
  if (!ring || !display) return;

  const avatars = Array.from(document.querySelectorAll('.orbit-avatar-wrapper'));
  
  const testimonials = [
    {
      badge: "A*", badgeClass: "pill--astar",
      quote: "Athenaeum transformed my O-Level preparation completely. The structured lessons and past-paper practice gave me the confidence I needed. I achieved A* in Biology!",
      name: "Fatima Anwar", detail: "O-Level Biology &bull; Cambridge Board",
      pill1: "A* Grade", pill2: "Biology"
    },
    {
      badge: "A", badgeClass: "pill--a",
      quote: "I was struggling with Matric Physics until I joined Athenaeum. The teachers explain every concept with real-world examples. I scored an A in my board exam!",
      name: "Ali Raza", detail: "Matric Physics &bull; Punjab Board",
      pill1: "A Grade", pill2: "Physics"
    },
    {
      badge: "A*", badgeClass: "pill--astar",
      quote: "The A-Level Math course here is exceptional. Detailed video lessons, instant doubt clearing and unlimited past papers — I scored A* and got into my dream university.",
      name: "Zara Khan", detail: "A-Level Mathematics &bull; Cambridge Board",
      pill1: "A* Grade", pill2: "Mathematics"
    },
    {
      badge: "A", badgeClass: "pill--a",
      quote: "FSc Chemistry was my biggest fear. After just 3 months with Athenaeum, I topped my class with an A. The animated lessons make organic chemistry feel easy!",
      name: "Hamza Siddiqui", detail: "FSc Chemistry &bull; Punjab Board",
      pill1: "A Grade", pill2: "Chemistry"
    },
    {
      badge: "A*", badgeClass: "pill--astar",
      quote: "I enrolled for O-Level English Literature and was amazed by the depth of analysis taught. The structured approach helped me achieve a perfect A* in my CAIE exam.",
      name: "Nadia Malik", detail: "O-Level English &bull; Cambridge Board",
      pill1: "A* Grade", pill2: "English Lit"
    },
    {
      badge: "A", badgeClass: "pill--a",
      quote: "Athenaeum's MDCAT preparation track is unmatched. The biology videos, MCQ banks and mock tests perfectly prepared me. I cleared MDCAT with a top percentile score!",
      name: "Usman Iqbal", detail: "MDCAT Prep &bull; Pre-Medical",
      pill1: "Top Score", pill2: "MDCAT"
    }
  ];

  let currentIndex = 0;
  let autoPlay;

  function setTestimonial(index) {
    const t = testimonials[index];
    
    // Rotate ring. We want the active avatar to face the right side (where the text is).
    // The avatars start from 0deg (top). The right side is at 90deg offset.
    // So to bring avatar `index` (which is at index * 60) to the 90deg position:
    const rotationAngle = -(index * 60) + 90;
    
    ring.style.transform = `rotate(${rotationAngle}deg)`;
    
    avatars.forEach(av => {
      // Counter-rotate the avatar so it stays upright
      av.querySelector('.orbit-avatar').style.setProperty('--current-ring-rotation', `${rotationAngle}deg`);
      av.querySelector('.orbit-avatar').classList.toggle('active', av.dataset.index == index);
    });

    // Fade out text, update, fade in
    display.classList.add('fade-out');
    setTimeout(() => {
      const badgeElem = document.getElementById('orb-badge');
      badgeElem.textContent = t.badge;
      if(t.badgeClass === 'pill--astar') {
         badgeElem.style.background = 'linear-gradient(135deg, #FF9800, #FF5722)';
         badgeElem.style.boxShadow = '0 4px 12px rgba(255, 152, 0, .3)';
      } else {
         badgeElem.style.background = 'linear-gradient(135deg, var(--clr-primary), var(--clr-secondary))';
         badgeElem.style.boxShadow = '0 4px 12px rgba(0, 210, 255, .3)';
      }

      document.getElementById('orb-quote').innerHTML = t.quote;
      document.getElementById('orb-name').textContent = t.name;
      document.getElementById('orb-detail').innerHTML = t.detail;
      
      const p1 = document.getElementById('orb-pill1');
      p1.textContent = t.pill1;
      p1.className = `result-pill ${t.badgeClass}`;
      
      document.getElementById('orb-pill2').textContent = t.pill2;
      
      display.classList.remove('fade-out');
    }, 400);

    currentIndex = index;
  }

  avatars.forEach(av => {
    av.addEventListener('click', () => {
      clearInterval(autoPlay);
      setTestimonial(parseInt(av.dataset.index));
      startAutoPlay();
    });
  });

  function startAutoPlay() {
    autoPlay = setInterval(() => {
      let next = currentIndex + 1;
      if (next >= testimonials.length) next = 0;
      setTestimonial(next);
    }, 5000);
  }

  // Init
  setTimeout(() => setTestimonial(0), 100);
  startAutoPlay();
})();

"""
    js = js[:js_start_idx] + new_js + js[js_end_idx:]
    with open('/Users/ali/Documents/Academy/main.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("JS updated.")

