import re

with open('/Users/ali/Documents/Academy/styles.css', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "/* ── 17. SUCCESS STORIES CAROUSEL ────────────────────────── */"
end_marker = "/* Grade summary bar */"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_css = """/* ── 17. SUCCESS STORIES CAROUSEL ────────────────────────── */
.stories {
  background: linear-gradient(180deg, var(--clr-white) 0%, var(--clr-surface-alt) 100%);
  padding: 80px 0;
}

/* Grade badges */
.badge-astar {
  background: linear-gradient(135deg, #FF9800, #FF5722);
  color: #fff;
  box-shadow: 0 4px 12px rgba(255, 152, 0, .3);
}

.badge-a {
  background: linear-gradient(135deg, var(--clr-primary), var(--clr-secondary));
  color: #fff;
  box-shadow: 0 4px 12px rgba(0, 210, 255, .3);
}

/* Carousel shell */
.carousel {
  overflow: hidden;
  position: relative;
  width: 100%;
  padding: 20px 0 40px;
}

.carousel-track {
  display: flex;
  gap: 30px;
  transition: transform 0.6s cubic-bezier(0.25, 1, 0.5, 1);
  will-change: transform;
}

/* Story card */
.story-card {
  flex: 0 0 calc(33.333% - 20px);
  min-width: 0;
  background: var(--clr-white);
  border-radius: var(--radius-xl);
  padding: 35px 30px 30px;
  box-shadow: 0 12px 36px rgba(0, 80, 136, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.8);
  position: relative;
  transition: box-shadow 0.4s ease, transform 0.4s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.story-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 6px;
  background: linear-gradient(90deg, var(--clr-secondary), var(--clr-purple));
  opacity: 0.8;
}

.story-card:hover {
  box-shadow: 0 20px 48px rgba(123, 44, 191, 0.12);
  transform: translateY(-8px);
}

.story-grade-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 4px 12px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-heading);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.5px;
  z-index: 2;
}

.story-quote {
  font-size: 15px;
  color: var(--clr-on-surface);
  line-height: 1.7;
  margin-bottom: var(--sp-6);
  flex-grow: 1;
  font-weight: 500;
  position: relative;
  z-index: 2;
}

.quote-mark {
  position: absolute;
  top: -20px;
  left: -15px;
  font-family: var(--font-heading);
  font-size: 8rem;
  line-height: 1;
  color: rgba(0, 210, 255, 0.07);
  z-index: 0;
  pointer-events: none;
}

.story-student {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  margin-bottom: var(--sp-4);
  position: relative;
  z-index: 2;
  border-top: 1px solid var(--clr-surface-high);
  padding-top: 20px;
}

.story-avatar {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  display: grid;
  place-items: center;
  font-size: 14px;
  font-weight: 800;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, .1);
}

.story-name {
  font-family: var(--font-heading);
  font-size: 16px;
  font-weight: 800;
  color: var(--clr-on-surface);
  line-height: 1.2;
}

.story-detail {
  font-size: 12px;
  color: var(--clr-on-surface-var);
  margin-top: 4px;
  font-weight: 500;
}

.story-result {
  display: flex;
  gap: var(--sp-2);
  flex-wrap: wrap;
  position: relative;
  z-index: 2;
}

.result-pill {
  display: inline-block;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.pill--astar {
  background: rgba(255, 152, 0, 0.1);
  color: #E65100;
}

.pill--a {
  background: rgba(0, 210, 255, 0.1);
  color: #0077b6;
}

.pill--subject {
  background: rgba(123, 44, 191, 0.08);
  color: var(--clr-purple);
}

/* Carousel controls */
.carousel-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  margin-top: 20px;
}

.carousel-btn {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full);
  border: none;
  background: var(--clr-white);
  color: var(--clr-primary);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 16px rgba(0, 80, 136, 0.1);
}

.carousel-btn .material-symbols-outlined {
  font-size: 20px;
  font-weight: 600;
}

.carousel-btn:hover {
  background: linear-gradient(135deg, var(--clr-secondary), var(--clr-primary));
  color: #fff;
  box-shadow: 0 8px 24px rgba(0, 210, 255, 0.3);
  transform: scale(1.1);
}

.carousel-dots {
  display: flex;
  gap: 8px;
  align-items: center;
}

.carousel-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background: var(--clr-border);
  border: none;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s ease;
}

.carousel-dot.active {
  background: var(--clr-secondary);
  width: 24px;
  box-shadow: 0 0 8px rgba(0, 210, 255, 0.5);
}

"""
    
    new_content = content[:start_idx] + new_css + content[end_idx:]
    with open('/Users/ali/Documents/Academy/styles.css', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Testimonial CSS updated successfully.")
else:
    print("Markers not found.")
