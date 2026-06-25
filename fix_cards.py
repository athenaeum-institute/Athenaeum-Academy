import re
import os

def rewrite_cards(filepath, is_matric=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the container
    content = re.sub(
        r'<div class="courses-grid" style="transform: scale\(0\.75\); transform-origin: top center; margin-bottom: -10%;">',
        '<div class="courses-catalog-grid">',
        content
    )
    
    # We will just replace the entire courses-catalog-grid block using a regex or simple split.
    start_str = '<div class="courses-catalog-grid">'
    end_str = '</div>\n      </div>\n    </section>'
    
    start_idx = content.find(start_str)
    end_idx = content.find(end_str, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        print(f"Failed to find grid block in {filepath}")
        return
        
    if not is_matric:
        new_cards = """
          <article class="course-card">
            <a href="course-details.html?id=c1" style="text-decoration: none; color: inherit; display: block; flex: 1;">
              <div class="course-thumb">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuAAhLHg64pwLVV8yaIMmFmOKWpzFsEaPTdPnkdGIick7vaGLVsyCm7lT3N31dSERzbEH_LW-75iNWgiLCf2472m6nKGW6izZQjtjILY59NK0w0vRh6I8e2H-3ON_BMoZCUoEzxPR0pb_pOLkSAHfc4lnNt3apVIL7_bNsR0e_Y3s-Ef4wuseHBP-HYRsEzBnc-nyX4azW05t730S46egrUwbwSn2zMoWhp0GEYRClI7lreMBg4z9pGZOOAucv-BN9FugORh9JIGWis" alt="A-Level Sciences" loading="lazy" />
                <span class="board-badge" style="background: #7B2FBE; color: white; border: none;">A Levels</span>
              </div>
              <div class="course-body">
                <h3 class="course-title">A-Level Sciences</h3>
                <div class="course-meta">
                  <span><span class="material-symbols-outlined" style="font-size:18px;">book</span> Sciences</span>
                </div>
                <div class="course-footer">
                  <span class="course-price">Rs 4,999</span>
                  <span style="font-size:0.8rem; background:#f0f9ff; color:#0284c7; padding:4px 8px; border-radius:12px; font-weight:600;">Demo Available</span>
                </div>
              </div>
            </a>
            <div style="display: flex; gap: 0.5rem; padding: 0 1.2rem 1.2rem 1.2rem;">
              <a href="trial-schedule.html?course=c1" class="btn" style="flex:1; justify-content:center; background:#eff6ff; color:var(--clr-primary); font-size:0.9rem; padding:0.6rem;">Free Trial</a>
              <a href="auth.html?mode=register&redirect=checkout.html?course=c1" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Enroll Now</a>
            </div>
          </article>

          <article class="course-card">
            <a href="course-details.html?id=c2" style="text-decoration: none; color: inherit; display: block; flex: 1;">
              <div class="course-thumb">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuADOmyQMRUv67kEVizDbtpxbOytz_Hg2ek4svWNOSw1HQnsF8CVXzhwlF3-dPDRuZSJ6HjMidKHCben8rLDCnL1RnaBcWeY9_USDhMhQ9XDKTmmCMgMMmyIqZXmbWujMCWgZO5F4idQ-CtHDUi-JDQobvW6iozwBiTFCKjBCwFv2BCr8Vyf0FTjkPTly5ctqbWMtcbs2PmYgcqQQkNpveBq-mTlSPsYXhDcvWTvtfkRk1C7gDQc91ATkCwp-lV2W-CEVT8LsRmBFdI" alt="O-Level Math" loading="lazy" />
                <span class="board-badge" style="background: #005088; color: white; border: none;">O Levels</span>
              </div>
              <div class="course-body">
                <h3 class="course-title">O-Level Math</h3>
                <div class="course-meta">
                  <span><span class="material-symbols-outlined" style="font-size:18px;">book</span> Mathematics</span>
                </div>
                <div class="course-footer">
                  <span class="course-price">Rs 4,999</span>
                  <span style="font-size:0.8rem; background:#f0f9ff; color:#0284c7; padding:4px 8px; border-radius:12px; font-weight:600;">Demo Available</span>
                </div>
              </div>
            </a>
            <div style="display: flex; gap: 0.5rem; padding: 0 1.2rem 1.2rem 1.2rem;">
              <a href="trial-schedule.html?course=c2" class="btn" style="flex:1; justify-content:center; background:#eff6ff; color:var(--clr-primary); font-size:0.9rem; padding:0.6rem;">Free Trial</a>
              <a href="auth.html?mode=register&redirect=checkout.html?course=c2" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Enroll Now</a>
            </div>
          </article>

          <article class="course-card">
            <a href="course-details.html?id=c3" style="text-decoration: none; color: inherit; display: block; flex: 1;">
              <div class="course-thumb">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCQLDTPXwkWB7YfSXWHTUtP7GyLSR2Va4AU-TuZmLUPc-dGy31jj_DkHdI2QAsyqGXN9LA5CCqpC0Gy0wd8E5iLKnUfHgr4TXaGalhNW6EkNoNUC9A5mp-TJ_-BvFrIpFc9OGrHgDOfqOqoWZ8OWBHi2ZBJWPyN_t_bBuqmFq91oGcCrGVxH7HD030RBTofs4BfawF22YjNIP4e7aS_qrQjapbsUnd7oWMSWoeEdO1O2yLD_ZwD7oWDqthgqzn9D4K2t3TRg8_z0E4" alt="English Language" loading="lazy" />
                <span class="board-badge" style="background: #005088; color: white; border: none;">O Levels</span>
              </div>
              <div class="course-body">
                <h3 class="course-title">English Language</h3>
                <div class="course-meta">
                  <span><span class="material-symbols-outlined" style="font-size:18px;">book</span> English</span>
                </div>
                <div class="course-footer">
                  <span class="course-price">Rs 4,999</span>
                  <span style="font-size:0.8rem; background:#f0f9ff; color:#0284c7; padding:4px 8px; border-radius:12px; font-weight:600;">Demo Available</span>
                </div>
              </div>
            </a>
            <div style="display: flex; gap: 0.5rem; padding: 0 1.2rem 1.2rem 1.2rem;">
              <a href="trial-schedule.html?course=c3" class="btn" style="flex:1; justify-content:center; background:#eff6ff; color:var(--clr-primary); font-size:0.9rem; padding:0.6rem;">Free Trial</a>
              <a href="auth.html?mode=register&redirect=checkout.html?course=c3" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Enroll Now</a>
            </div>
          </article>

          <article class="course-card">
            <a href="course-details.html?id=c4" style="text-decoration: none; color: inherit; display: block; flex: 1;">
              <div class="course-thumb">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuBWvWbai5tAsnOuxB6ZzstE45h38glpROI-boGmmlts2-vnS6OsCZDw-gRO8C3JcOGXjyylOG--m5MWJI_IYJv63w-_B5PTaKEPIa_3bAQF2WT1qYSip9wlAp2mBGGOfRh2E13m2qS1TcbilOGEADq3Ge4Dmn2mlKEWefax1t-en4RPca-3WeiF21E-uUEA47_yJaFJYmGslnORGhrxLpzmBEpehnMbFs_WYHwM5nP-b6HvdH2_mhUqqb-PA-5OhKurI-Rp5EoA7uA" alt="Pakistan Studies" loading="lazy" />
                <span class="board-badge" style="background: #005088; color: white; border: none;">O Levels</span>
              </div>
              <div class="course-body">
                <h3 class="course-title">Pakistan Studies</h3>
                <div class="course-meta">
                  <span><span class="material-symbols-outlined" style="font-size:18px;">book</span> Social Studies</span>
                </div>
                <div class="course-footer">
                  <span class="course-price">Rs 4,999</span>
                  <span style="font-size:0.8rem; background:#f0f9ff; color:#0284c7; padding:4px 8px; border-radius:12px; font-weight:600;">Demo Available</span>
                </div>
              </div>
            </a>
            <div style="display: flex; gap: 0.5rem; padding: 0 1.2rem 1.2rem 1.2rem;">
              <a href="trial-schedule.html?course=c4" class="btn" style="flex:1; justify-content:center; background:#eff6ff; color:var(--clr-primary); font-size:0.9rem; padding:0.6rem;">Free Trial</a>
              <a href="auth.html?mode=register&redirect=checkout.html?course=c4" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Enroll Now</a>
            </div>
          </article>
"""
    else:
        new_cards = """
          <article class="course-card">
            <a href="course-details.html?id=m1" style="text-decoration: none; color: inherit; display: block; flex: 1;">
              <div class="course-thumb">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuD4kNe2toxyjE5ZBGUbLnYb8xkq2BU7IbNMtDZE-pbnobo0WqMzpw2OUzQUbffyND0mJZcNBTSXKCg-X6KWGllujYqfy8TCA3TTj2kSqZDerkTgRZW5tTw1x-kKeG69wbtvAksylDZQYAZdMoOqksE-reVaqT8MUVuXE6fEcDjtYCmOBd8-fYOMkX7XhdNShwyUKKMKWyymjZrdb6CmUv-p5VXTCshdJzl2q-FVxhoCU0Fw_I4nk6juz8DyHxk1DUbi2HKfzu2_-wc" alt="Matric Mathematics" loading="lazy" />
                <span class="board-badge" style="background: #00A86B; color: white; border: none;">Matric</span>
              </div>
              <div class="course-body">
                <h3 class="course-title">Matric Mathematics (Science)</h3>
                <div class="course-meta">
                  <span><span class="material-symbols-outlined" style="font-size:18px;">book</span> Mathematics</span>
                </div>
                <div class="course-footer">
                  <span class="course-price">Rs 2,999</span>
                  <span style="font-size:0.8rem; background:#f0f9ff; color:#0284c7; padding:4px 8px; border-radius:12px; font-weight:600;">Demo Available</span>
                </div>
              </div>
            </a>
            <div style="display: flex; gap: 0.5rem; padding: 0 1.2rem 1.2rem 1.2rem;">
              <a href="trial-schedule.html?course=m1" class="btn" style="flex:1; justify-content:center; background:#eff6ff; color:var(--clr-primary); font-size:0.9rem; padding:0.6rem;">Free Trial</a>
              <a href="auth.html?mode=register&redirect=checkout.html?course=m1" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Enroll Now</a>
            </div>
          </article>

          <article class="course-card">
            <a href="course-details.html?id=m2" style="text-decoration: none; color: inherit; display: block; flex: 1;">
              <div class="course-thumb">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuD4kNe2toxyjE5ZBGUbLnYb8xkq2BU7IbNMtDZE-pbnobo0WqMzpw2OUzQUbffyND0mJZcNBTSXKCg-X6KWGllujYqfy8TCA3TTj2kSqZDerkTgRZW5tTw1x-kKeG69wbtvAksylDZQYAZdMoOqksE-reVaqT8MUVuXE6fEcDjtYCmOBd8-fYOMkX7XhdNShwyUKKMKWyymjZrdb6CmUv-p5VXTCshdJzl2q-FVxhoCU0Fw_I4nk6juz8DyHxk1DUbi2HKfzu2_-wc" alt="Matric Physics" loading="lazy" />
                <span class="board-badge" style="background: #00A86B; color: white; border: none;">Matric</span>
              </div>
              <div class="course-body">
                <h3 class="course-title">Matric Physics</h3>
                <div class="course-meta">
                  <span><span class="material-symbols-outlined" style="font-size:18px;">book</span> Physics</span>
                </div>
                <div class="course-footer">
                  <span class="course-price">Rs 2,999</span>
                  <span style="font-size:0.8rem; background:#f0f9ff; color:#0284c7; padding:4px 8px; border-radius:12px; font-weight:600;">Demo Available</span>
                </div>
              </div>
            </a>
            <div style="display: flex; gap: 0.5rem; padding: 0 1.2rem 1.2rem 1.2rem;">
              <a href="trial-schedule.html?course=m2" class="btn" style="flex:1; justify-content:center; background:#eff6ff; color:var(--clr-primary); font-size:0.9rem; padding:0.6rem;">Free Trial</a>
              <a href="auth.html?mode=register&redirect=checkout.html?course=m2" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Enroll Now</a>
            </div>
          </article>

          <article class="course-card">
            <a href="course-details.html?id=m3" style="text-decoration: none; color: inherit; display: block; flex: 1;">
              <div class="course-thumb">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuD4kNe2toxyjE5ZBGUbLnYb8xkq2BU7IbNMtDZE-pbnobo0WqMzpw2OUzQUbffyND0mJZcNBTSXKCg-X6KWGllujYqfy8TCA3TTj2kSqZDerkTgRZW5tTw1x-kKeG69wbtvAksylDZQYAZdMoOqksE-reVaqT8MUVuXE6fEcDjtYCmOBd8-fYOMkX7XhdNShwyUKKMKWyymjZrdb6CmUv-p5VXTCshdJzl2q-FVxhoCU0Fw_I4nk6juz8DyHxk1DUbi2HKfzu2_-wc" alt="Matric Chemistry" loading="lazy" />
                <span class="board-badge" style="background: #00A86B; color: white; border: none;">Matric</span>
              </div>
              <div class="course-body">
                <h3 class="course-title">Matric Chemistry</h3>
                <div class="course-meta">
                  <span><span class="material-symbols-outlined" style="font-size:18px;">book</span> Chemistry</span>
                </div>
                <div class="course-footer">
                  <span class="course-price">Rs 2,999</span>
                  <span style="font-size:0.8rem; background:#f0f9ff; color:#0284c7; padding:4px 8px; border-radius:12px; font-weight:600;">Demo Available</span>
                </div>
              </div>
            </a>
            <div style="display: flex; gap: 0.5rem; padding: 0 1.2rem 1.2rem 1.2rem;">
              <a href="trial-schedule.html?course=m3" class="btn" style="flex:1; justify-content:center; background:#eff6ff; color:var(--clr-primary); font-size:0.9rem; padding:0.6rem;">Free Trial</a>
              <a href="auth.html?mode=register&redirect=checkout.html?course=m3" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Enroll Now</a>
            </div>
          </article>

          <article class="course-card">
            <a href="course-details.html?id=m4" style="text-decoration: none; color: inherit; display: block; flex: 1;">
              <div class="course-thumb">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuD4kNe2toxyjE5ZBGUbLnYb8xkq2BU7IbNMtDZE-pbnobo0WqMzpw2OUzQUbffyND0mJZcNBTSXKCg-X6KWGllujYqfy8TCA3TTj2kSqZDerkTgRZW5tTw1x-kKeG69wbtvAksylDZQYAZdMoOqksE-reVaqT8MUVuXE6fEcDjtYCmOBd8-fYOMkX7XhdNShwyUKKMKWyymjZrdb6CmUv-p5VXTCshdJzl2q-FVxhoCU0Fw_I4nk6juz8DyHxk1DUbi2HKfzu2_-wc" alt="Matric Biology" loading="lazy" />
                <span class="board-badge" style="background: #00A86B; color: white; border: none;">Matric</span>
              </div>
              <div class="course-body">
                <h3 class="course-title">Matric Biology</h3>
                <div class="course-meta">
                  <span><span class="material-symbols-outlined" style="font-size:18px;">book</span> Biology</span>
                </div>
                <div class="course-footer">
                  <span class="course-price">Rs 2,999</span>
                  <span style="font-size:0.8rem; background:#f0f9ff; color:#0284c7; padding:4px 8px; border-radius:12px; font-weight:600;">Demo Available</span>
                </div>
              </div>
            </a>
            <div style="display: flex; gap: 0.5rem; padding: 0 1.2rem 1.2rem 1.2rem;">
              <a href="trial-schedule.html?course=m4" class="btn" style="flex:1; justify-content:center; background:#eff6ff; color:var(--clr-primary); font-size:0.9rem; padding:0.6rem;">Free Trial</a>
              <a href="auth.html?mode=register&redirect=checkout.html?course=m4" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Enroll Now</a>
            </div>
          </article>
"""

    new_content = content[:start_idx + len(start_str)] + "\n" + new_cards + content[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated {filepath}")

rewrite_cards('/Users/ali/Documents/Academy/oa-levels.html', is_matric=False)
rewrite_cards('/Users/ali/Documents/Academy/matric-inter.html', is_matric=True)
