import re

with open("index.html", "r") as f:
    index_html = f.read()

# Extract head, navbar, footer
head_match = re.search(r'(<head>.*?</head>)', index_html, re.DOTALL)
head = head_match.group(1) if head_match else ""

nav_match = re.search(r'(<header id="navbar" class="navbar">.*?</header>)', index_html, re.DOTALL)
navbar = nav_match.group(1) if nav_match else ""

footer_match = re.search(r'(<footer class="footer">.*?</html>)', index_html, re.DOTALL)
footer = footer_match.group(1) if footer_match else ""

# Modify the active state in navbar based on page
def get_navbar(page):
    nav = navbar
    nav = nav.replace('class="nav-link active"', 'class="nav-link"')
    if page == "oa":
        nav = nav.replace('href="oa-levels.html" class="nav-link"', 'href="oa-levels.html" class="nav-link active"')
    elif page == "matric":
        nav = nav.replace('href="matric-inter.html" class="nav-link"', 'href="matric-inter.html" class="nav-link active"')
    return nav

# Course card HTML structure based on index.html
def get_course_card(title, img_url, duration, badge, instructor, rating, students):
    return f'''          <article class="course-card">
            <a href="course-details.html" style="text-decoration: none; color: inherit;">
            <div class="course-thumb">
              <img src="{img_url}" alt="{title}" loading="lazy" />
              <span class="duration-badge">{duration}</span>
              <span class="board-badge{' board-badge--inter' if badge == 'INTER' else ''}">{badge}</span>
            </div>
            <div class="course-body">
              <div class="stars">★★★★★<span class="rating-text">({rating})</span></div>
              <h3 class="course-title">{title}</h3>
              <div class="course-meta">
                <span><span class="material-symbols-outlined">person</span> {students}+</span>
                <span><span class="material-symbols-outlined">school</span> Beginner</span>
              </div>
              <div class="course-footer">
                <div class="instructor">
                  <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuD4kNe2toxyjE5ZBGUbLnYb8xkq2BU7IbNMtDZE-pbnobo0WqMzpw2OUzQUbffyND0mJZcNBTSXKCg-X6KWGllujYqfy8TCA3TTj2kSqZDerkTgRZW5tTw1x-kKeG69wbtvAksylDZQYAZdMoOqksE-reVaqT8MUVuXE6fEcDjtYCmOBd8-fYOMkX7XhdNShwyUKKMKWyymjZrdb6CmUv-p5VXTCshdJzl2q-FVxhoCU0Fw_I4nk6juz8DyHxk1DUbi2HKfzu2_-wc" alt="{instructor}" class="instructor-avatar" />
                  <span>{instructor}</span>
                </div>
                <span class="course-price" style="color: var(--clr-secondary); font-weight: 800;">FREE</span>
              </div>
            </div>
            </a>
          </article>'''

oa_courses = [
    get_course_card("A-Level Sciences", "https://lh3.googleusercontent.com/aida-public/AB6AXuAAhLHg64pwLVV8yaIMmFmOKWpzFsEaPTdPnkdGIick7vaGLVsyCm7lT3N31dSERzbEH_LW-75iNWgiLCf2472m6nKGW6izZQjtjILY59NK0w0vRh6I8e2H-3ON_BMoZCUoEzxPR0pb_pOLkSAHfc4lnNt3apVIL7_bNsR0e_Y3s-Ef4wuseHBP-HYRsEzBnc-nyX4azW05t730S46egrUwbwSn2zMoWhp0GEYRClI7lreMBg4z9pGZOOAucv-BN9FugORh9JIGWis", "12 WEEKS", "CAMBRIDGE", "Prof. Maria Khan", "4.9", "150"),
    get_course_card("O-Level Math", "https://lh3.googleusercontent.com/aida-public/AB6AXuADOmyQMRUv67kEVizDbtpxbOytz_Hg2ek4svWNOSw1HQnsF8CVXzhwlF3-dPDRuZSJ6HjMidKHCben8rLDCnL1RnaBcWeY9_USDhMhQ9XDKTmmCMgMMmyIqZXmbWujMCWgZO5F4idQ-CtHDUi-JDQobvW6iozwBiTFCKjBCwFv2BCr8Vyf0FTjkPTly5ctqbWMtcbs2PmYgcqQQkNpveBq-mTlSPsYXhDcvWTvtfkRk1C7gDQc91ATkCwp-lV2W-CEVT8LsRmBFdI", "10 WEEKS", "CAMBRIDGE", "Prof. Sarah Jenkins", "5.0", "200"),
    get_course_card("English Language", "https://lh3.googleusercontent.com/aida-public/AB6AXuCQLDTPXwkWB7YfSXWHTUtP7GyLSR2Va4AU-TuZmLUPc-dGy31jj_DkHdI2QAsyqGXN9LA5CCqpC0Gy0wd8E5iLKnUfHgr4TXaGalhNW6EkNoNUC9A5mp-TJ_-BvFrIpFc9OGrHgDOfqOqoWZ8OWBHi2ZBJWPyN_t_bBuqmFq91oGcCrGVxH7HD030RBTofs4BfawF22YjNIP4e7aS_qrQjapbsUnd7oWMSWoeEdO1O2yLD_ZwD7oWDqthgqzn9D4K2t3TRg8_z0E4", "08 WEEKS", "CAMBRIDGE", "Prof. Ahmed Ali", "4.8", "180"),
    get_course_card("Pakistan Studies", "https://lh3.googleusercontent.com/aida-public/AB6AXuBWvWbai5tAsnOuxB6ZzstE45h38glpROI-boGmmlts2-vnS6OsCZDw-gRO8C3JcOGXjyylOG--m5MWJI_IYJv63w-_B5PTaKEPIa_3bAQF2WT1qYSip9wlAp2mBGGOfRh2E13m2qS1TcbilOGEADq3Ge4Dmn2mlKEWefax1t-en4RPca-3WeiF21E-uUEA47_yJaFJYmGslnORGhrxLpzmBEpehnMbFs_WYHwM5nP-b6HvdH2_mhUqqb-PA-5OhKurI-Rp5EoA7uA", "06 WEEKS", "CAMBRIDGE", "Prof. Sana", "4.9", "120")
]

matric_courses = [
    get_course_card("Matric Physics", "https://lh3.googleusercontent.com/aida-public/AB6AXuCQLDTPXwkWB7YfSXWHTUtP7GyLSR2Va4AU-TuZmLUPc-dGy31jj_DkHdI2QAsyqGXN9LA5CCqpC0Gy0wd8E5iLKnUfHgr4TXaGalhNW6EkNoNUC9A5mp-TJ_-BvFrIpFc9OGrHgDOfqOqoWZ8OWBHi2ZBJWPyN_t_bBuqmFq91oGcCrGVxH7HD030RBTofs4BfawF22YjNIP4e7aS_qrQjapbsUnd7oWMSWoeEdO1O2yLD_ZwD7oWDqthgqzn9D4K2t3TRg8_z0E4", "12 WEEKS", "MATRIC", "Prof. Ahmed Ali", "4.8", "150"),
    get_course_card("Matric Biology", "https://lh3.googleusercontent.com/aida-public/AB6AXuAAhLHg64pwLVV8yaIMmFmOKWpzFsEaPTdPnkdGIick7vaGLVsyCm7lT3N31dSERzbEH_LW-75iNWgiLCf2472m6nKGW6izZQjtjILY59NK0w0vRh6I8e2H-3ON_BMoZCUoEzxPR0pb_pOLkSAHfc4lnNt3apVIL7_bNsR0e_Y3s-Ef4wuseHBP-HYRsEzBnc-nyX4azW05t730S46egrUwbwSn2zMoWhp0GEYRClI7lreMBg4z9pGZOOAucv-BN9FugORh9JIGWis", "14 WEEKS", "MATRIC", "Prof. Maria Khan", "4.9", "120"),
    get_course_card("Intermediate Chemistry", "https://lh3.googleusercontent.com/aida-public/AB6AXuBWvWbai5tAsnOuxB6ZzstE45h38glpROI-boGmmlts2-vnS6OsCZDw-gRO8C3JcOGXjyylOG--m5MWJI_IYJv63w-_B5PTaKEPIa_3bAQF2WT1qYSip9wlAp2mBGGOfRh2E13m2qS1TcbilOGEADq3Ge4Dmn2mlKEWefax1t-en4RPca-3WeiF21E-uUEA47_yJaFJYmGslnORGhrxLpzmBEpehnMbFs_WYHwM5nP-b6HvdH2_mhUqqb-PA-5OhKurI-Rp5EoA7uA", "14 WEEKS", "INTER", "Prof. Sana", "4.8", "120"),
    get_course_card("Pre-Engineering Physics", "https://lh3.googleusercontent.com/aida-public/AB6AXuADOmyQMRUv67kEVizDbtpxbOytz_Hg2ek4svWNOSw1HQnsF8CVXzhwlF3-dPDRuZSJ6HjMidKHCben8rLDCnL1RnaBcWeY9_USDhMhQ9XDKTmmCMgMMmyIqZXmbWujMCWgZO5F4idQ-CtHDUi-JDQobvW6iozwBiTFCKjBCwFv2BCr8Vyf0FTjkPTly5ctqbWMtcbs2PmYgcqQQkNpveBq-mTlSPsYXhDcvWTvtfkRk1C7gDQc91ATkCwp-lV2W-CEVT8LsRmBFdI", "16 WEEKS", "INTER", "Prof. Sarah Jenkins", "5.0", "200")
]

oa_html = f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
{head.replace("<title>Athenaeum | Master O/A Levels, Matric &amp; Inter</title>", "<title>Athenaeum | O/A Levels</title>")}
<body>
{get_navbar("oa")}
  <main style="padding-top: 80px;">
    <section class="hero" id="hero" style="min-height: 40vh; display: flex; align-items: center; padding: 4rem 0;">
      <div class="hero-blob hero-blob--1"></div>
      <div class="hero-blob hero-blob--2"></div>
      <div class="container hero-grid" style="grid-template-columns: 1fr; text-align: center;">
        <div class="hero-copy" style="margin: 0 auto; display: flex; flex-direction: column; align-items: center;">
          <h1 class="hero-title" style="font-size: 3rem;">
            Master Your CAIE Exams with <span class="accent-text">Expert Guidance.</span>
          </h1>
          <p class="section-subtitle" style="margin-top: 1rem; max-width: 600px;">
            World-class Cambridge curriculum taught by specialist educators to help you secure top grades.
          </p>
        </div>
      </div>
    </section>

    <section class="courses section" id="courses">
      <div class="container">
        <div class="section-header">
          <span class="section-eyebrow">Cambridge Excellence</span>
          <h2 class="section-title center">O/A Level Subjects</h2>
        </div>
        <div class="courses-grid" style="transform: scale(0.75); transform-origin: top center; margin-bottom: -10%;">
{"".join(oa_courses)}
        </div>
      </div>
    </section>
  </main>
{footer}
'''

matric_html = f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
{head.replace("<title>Athenaeum | Master O/A Levels, Matric &amp; Inter</title>", "<title>Athenaeum | Matric/Inter</title>")}
<body>
{get_navbar("matric")}
  <main style="padding-top: 80px;">
    <section class="hero" id="hero" style="min-height: 40vh; display: flex; align-items: center; padding: 4rem 0;">
      <div class="hero-blob hero-blob--1"></div>
      <div class="hero-blob hero-blob--2"></div>
      <div class="container hero-grid" style="grid-template-columns: 1fr; text-align: center;">
        <div class="hero-copy" style="margin: 0 auto; display: flex; flex-direction: column; align-items: center;">
          <h1 class="hero-title" style="font-size: 3rem;">
            Top Board Positions <span class="accent-text">Start Here.</span>
          </h1>
          <p class="section-subtitle" style="margin-top: 1rem; max-width: 600px;">
            Dedicated programs for Punjab, Sindh, and Federal Board students designed for academic excellence.
          </p>
        </div>
      </div>
    </section>

    <section class="courses section" id="courses">
      <div class="container">
        <div class="section-header">
          <span class="section-eyebrow">Local Board Excellence</span>
          <h2 class="section-title center">Matric & Intermediate Subjects</h2>
        </div>
        <div class="courses-grid" style="transform: scale(0.75); transform-origin: top center; margin-bottom: -10%;">
{"".join(matric_courses)}
        </div>
      </div>
    </section>
  </main>
{footer}
'''

with open("oa-levels.html", "w") as f:
    f.write(oa_html)

with open("matric-inter.html", "w") as f:
    f.write(matric_html)

print("Pages generated successfully.")
