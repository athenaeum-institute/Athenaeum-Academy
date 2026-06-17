/* ============================================================
   Athenaeum — JavaScript
   Handles: navbar scroll, mobile menu, tab switching, animations
============================================================ */

// ── Navbar: add "scrolled" class on scroll ──────────────────
const navbar = document.getElementById('navbar');
let navTicking = false;

window.addEventListener('scroll', () => {
  if (!navTicking) {
    window.requestAnimationFrame(() => {
      navbar.classList.toggle('scrolled', window.scrollY > 40);
      navTicking = false;
    });
    navTicking = true;
  }
}, { passive: true });

// ── Mobile hamburger ────────────────────────────────────────
const hamburger    = document.getElementById('hamburger');
const mobileDrawer = document.getElementById('mobile-drawer');

hamburger.addEventListener('click', () => {
  const isOpen = hamburger.classList.toggle('open');
  mobileDrawer.classList.toggle('open', isOpen);
  hamburger.setAttribute('aria-expanded', isOpen);
});

// Close drawer on nav link click
mobileDrawer.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', () => {
    hamburger.classList.remove('open');
    mobileDrawer.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
  });
});

// ── Active nav link tracking ────────────────────────────────
const sections  = document.querySelectorAll('section[id]');
const navLinks  = document.querySelectorAll('.nav-link');

const sectionObserver = new IntersectionObserver(
  entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinks.forEach(link => {
          link.classList.toggle('active',
            link.getAttribute('href') === `#${entry.target.id}`
          );
        });
      }
    });
  },
  { rootMargin: '-40% 0px -55% 0px' }
);

sections.forEach(section => sectionObserver.observe(section));

// ── Matric / Inter tabs ─────────────────────────────────────
(function initMatricTabs() {
  const tabBtns  = document.querySelectorAll('#matric-tabs .tab-btn');
  const panels   = document.querySelectorAll('.matric-panel');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;

      tabBtns.forEach(b => b.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      document.getElementById(`panel-${target}`).classList.add('active');
    });
  });
})();

// ── Course filter tabs (visual only) ───────────────────────
(function initCourseTabs() {
  const tabBtns = document.querySelectorAll('#course-tabs .tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });
})();

// ── Scroll-reveal animation ─────────────────────────────────
const style = document.createElement('style');
style.textContent = `
  .reveal        { opacity: 0; transform: translateY(32px); transition: opacity 0.6s ease, transform 0.6s ease; }
  .reveal.visible { opacity: 1; transform: translateY(0); }
`;
document.head.appendChild(style);

// Add reveal class to target elements
const revealTargets = [
  '.hero-copy',
  '.hero-visual',
  '.feature-item',
  '.oa-card',
  '.matric-card',
  '.course-card',
  '.stat-item',
  '.about-copy',
  '.about-visual',
  '.contact-copy',
  '.contact-form',
  '.section-header',
];

document.querySelectorAll(revealTargets.join(', ')).forEach(el => {
  el.classList.add('reveal');
});

const revealObserver = new IntersectionObserver(
  entries => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        // Staggered delay for grid items
        const delay = (entry.target.dataset.delay || 0) * 80;
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, delay);
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.1 }
);

// Add stagger data attributes to grid children
document.querySelectorAll(
  '.oa-grid, .matric-grid, .courses-grid, .stats-grid, .feature-grid'
).forEach(grid => {
  Array.from(grid.children).forEach((child, idx) => {
    child.dataset.delay = idx;
  });
});

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// ── Contact form (demo) ─────────────────────────────────────
const contactForm = document.getElementById('contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', e => {
    e.preventDefault();
    const btn = contactForm.querySelector('#contact-submit');
    const original = btn.innerHTML;
    btn.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Message Sent!';
    btn.style.background = 'var(--clr-secondary)';
    btn.disabled = true;
    setTimeout(() => {
      btn.innerHTML = original;
      btn.style.background = '';
      btn.disabled = false;
      contactForm.reset();
    }, 3500);
  });
}

// ── Micro-interactions: button ripple ──────────────────────
document.querySelectorAll('.btn').forEach(btn => {
  btn.addEventListener('click', function(e) {
    const ripple = document.createElement('span');
    const rect   = this.getBoundingClientRect();
    const size   = Math.max(rect.width, rect.height);
    const x      = e.clientX - rect.left - size / 2;
    const y      = e.clientY - rect.top  - size / 2;

    Object.assign(ripple.style, {
      position:       'absolute',
      width:          `${size}px`,
      height:         `${size}px`,
      left:           `${x}px`,
      top:            `${y}px`,
      background:     'rgba(255,255,255,.3)',
      borderRadius:   '50%',
      transform:      'scale(0)',
      animation:      'ripple-anim 0.55s ease-out forwards',
      pointerEvents:  'none',
    });

    this.style.position = 'relative';
    this.style.overflow = 'hidden';
    this.appendChild(ripple);
    ripple.addEventListener('animationend', () => ripple.remove());
  });
});

const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
  @keyframes ripple-anim {
    to { transform: scale(2.5); opacity: 0; }
  }
`;
document.head.appendChild(rippleStyle);

// ── Smooth scroll polyfill fallback ────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = 80; // navbar height
      const top    = target.getBoundingClientRect().top + window.pageYOffset - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

// ── Orbit Testimonial System ────────────────────────────────
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

// ── WhatsApp Floating Widget ────────────────────────────────
(function initWAWidget() {
  const fab     = document.getElementById('wa-fab');
  const tooltip = document.getElementById('wa-tooltip');
  const closeBtn = document.getElementById('wa-close');
  const badge   = document.querySelector('.wa-fab-badge');
  if (!fab || !tooltip) return;

  function openTooltip() {
    tooltip.classList.add('open');
    if (badge) badge.style.display = 'none';
    fab.setAttribute('aria-expanded', 'true');
  }

  function closeTooltip() {
    tooltip.classList.remove('open');
    fab.setAttribute('aria-expanded', 'false');
  }

  fab.addEventListener('click', () => {
    if (tooltip.classList.contains('open')) closeTooltip();
    else openTooltip();
  });

  if (closeBtn) closeBtn.addEventListener('click', closeTooltip);

  // Close when clicking outside
  document.addEventListener('click', e => {
    if (!fab.contains(e.target) && !tooltip.contains(e.target)) {
      closeTooltip();
    }
  });

  // Auto-open once after 8 seconds (first visit feel)
  const hasOpened = sessionStorage.getItem('wa_opened');
  if (!hasOpened) {
    setTimeout(() => {
      openTooltip();
      sessionStorage.setItem('wa_opened', '1');
    }, 8000);
  }
})();

console.log('🎓 Athenaeum JS loaded successfully');



// ── Scroll Progress Bar ─────────────────────────────────────
(function initScrollProgress() {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;

  const container = document.createElement('div');
  container.className = 'scroll-progress-container';
  
  const bar = document.createElement('div');
  bar.className = 'scroll-progress-bar';
  bar.id = 'scroll-progress-bar';
  bar.style.transformOrigin = 'left'; // Ensure scaling from left
  
  container.appendChild(bar);
  navbar.appendChild(container);

  let ticking = false;
  let scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;

  // Recalculate layout metrics only on resize or layout shifts, not on scroll
  window.addEventListener('resize', () => {
    scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
  }, { passive: true });

  window.addEventListener('scroll', () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
        
        let scrolled = scrollHeight > 0 ? (winScroll / scrollHeight) : 0;
        if (scrolled > 1) scrolled = 1;
        if (scrolled < 0) scrolled = 0;
        
        bar.style.transform = `scaleX(${scrolled})`;
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
})();

// ── Global Course Card Routing ────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.course-card, .course-item');
  cards.forEach((card, index) => {
    // Check if it already has an anchor tag routing
    if (card.querySelector('a') && card.classList.contains('course-card')) return;
    
    // Assign id based on index for dummy routing
    const courseId = (index % 8) + 1;
    card.style.cursor = 'pointer';
    card.addEventListener('click', () => {
      window.location.href = `course-details.html?id=${courseId}`;
    });
  });
});






// ============================================================
// NATURAL DESKTOP DRAG-TO-SCROLL & WHEEL (COURSES GRID)
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
  const grids = document.querySelectorAll(".courses-grid");
  grids.forEach(grid => {
    let isDown = false;
    let startX;
    let scrollLeft;

    grid.style.cursor = "grab";

    grid.addEventListener("mousedown", (e) => {
      isDown = true;
      grid.style.cursor = "grabbing";
      grid.style.userSelect = "none"; 
      startX = e.pageX - grid.offsetLeft;
      scrollLeft = grid.scrollLeft;
    });

    grid.addEventListener("mouseleave", () => {
      isDown = false;
      grid.style.cursor = "grab";
      grid.style.userSelect = "auto";
    });

    grid.addEventListener("mouseup", () => {
      isDown = false;
      grid.style.cursor = "grab";
      grid.style.userSelect = "auto";
    });

    grid.addEventListener("mousemove", (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - grid.offsetLeft;
      const walk = (x - startX); // Exact 1:1 movement for natural feel
      grid.scrollLeft = scrollLeft - walk;
    });

    grid.addEventListener("wheel", (e) => {
      // Allow vertical scroll wheel to scroll horizontal if hovering
      if (Math.abs(e.deltaY) > 0 && e.deltaX === 0) {
        // Prevent default only if we haven reached the edge
        const atStart = grid.scrollLeft === 0 && e.deltaY < 0;
        const atEnd = grid.scrollLeft >= (grid.scrollWidth - grid.clientWidth) && e.deltaY > 0;
        
        if (!atStart && !atEnd) {
          e.preventDefault();
          grid.scrollLeft += e.deltaY;
        }
      }
    });
    
    // Disable drag on images/links to prevent dragging ghosts
    grid.querySelectorAll("img, a").forEach(el => {
      el.addEventListener("dragstart", (e) => {
        e.preventDefault();
      });
    });
  });
});
