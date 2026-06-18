import re

# 1. UPDATE dashboard.css
with open('/Users/ali/Documents/Academy/dashboard.css', 'r') as f:
    css = f.read()

css = css.replace('--header-height: 70px;', '--header-height: 60px;')
css = css.replace('padding: 60px 24px;', 'padding: 30px 24px;')

# Sidebar background to Indigo
css = re.sub(r'\.sidebar\s*\{[^}]*background:[^;]+;', lambda m: m.group(0).replace('var(--clr-primary-dark)', '#0A0E27'), css)

# Hover glow
if 'text-shadow: 0 0 12px' not in css:
    css = css.replace('.nav-item:hover, .nav-item.active {', 
                      '.nav-item:hover, .nav-item.active {\n  color: white;\n  background: rgba(255,255,255,0.05);\n  border-left-color: var(--clr-secondary);\n}\n.nav-item:hover .material-symbols-outlined, .nav-item.active .material-symbols-outlined {\n  text-shadow: 0 0 12px rgba(0, 210, 255, 0.8);\n  color: var(--clr-secondary);\n')

with open('/Users/ali/Documents/Academy/dashboard.css', 'w') as f:
    f.write(css)

# 2. UPDATE dashboard-student.html
with open('/Users/ali/Documents/Academy/dashboard-student.html', 'r') as f:
    html = f.read()

# We need to replace the style block between /* ── CUSTOM UI MODS FOR STUDENT DASHBOARD ── */ and </style>
new_styles = """    /* ── CUSTOM UI MODS FOR STUDENT DASHBOARD (REDESIGNED) ── */
    :root {
      --primary: #005088;
      --accent: #00D2FF;
      --gold: #FFD700;
      /* Vibrant EdTech Light Theme */
      --bg: #F4F7FB;
      --card: #FFFFFF;
      --border: #E2E8F0;
      --text: #1E293B;
      --muted: #64748B;
      --green: #10B981;
      --orange: #F97316;
      --purple: #8B5CF6;
    }
    
    body { background-color: var(--bg); color: var(--text); }
    
    /* Animations */
    .fade-in { animation: fadeIn 0.4s ease forwards; opacity: 0; }
    @keyframes fadeIn { from{opacity:0;transform:translateY(5px)} to{opacity:1;transform:translateY(0)} }
    
    /* Skeletons */
    .skeleton { background: linear-gradient(90deg, #e2e8f0 25%, #cbd5e1 50%, #e2e8f0 75%); background-size: 200% 100%; animation: loading 1.5s infinite; border-radius: 8px; color:transparent!important; min-height: 20px;}
    .skeleton * { visibility: hidden; }
    @keyframes loading { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
    
    /* Custom XP Progress */
    .xp-progress-bar { width: 100%; height: 6px; background: var(--bg); border-radius: 4px; overflow: hidden; margin-top: 0.5rem; }
    .xp-progress-fill { height: 100%; background: linear-gradient(90deg, var(--purple), var(--accent)); transition: width 1s cubic-bezier(.175,.885,.32,1.275); width: 0%; }
    
    /* Badges */
    .badge-premium { background: rgba(255,215,0,0.15); color: #d97706; border: 1px solid rgba(255,215,0,0.3); }
    .badge-trial { background: rgba(210,153,34,0.15); color: #d29922; border: 1px solid rgba(210,153,34,0.3); }
    .badge-level { background: rgba(139,92,246,0.1); color: var(--purple); border: 1px solid rgba(139,92,246,0.2); padding: 2px 8px; font-size: 0.75rem; border-radius: 12px; font-weight:700;}
    
    /* Grid Layouts - Micro Cards */
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
    .stat-card { background: var(--card); border: 1px solid var(--border); padding: 1rem; border-radius: 12px; display: flex; flex-direction: column; gap: 0.25rem; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.02); position: relative; overflow:hidden; }
    .stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); }
    .stat-val { font-size: 1.6rem; font-weight: 800; font-family: 'Urbanist', sans-serif; color: var(--text); line-height: 1.1; }
    .stat-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }
    
    /* Glowing Bottom Accent Lines */
    .stat-card::after { content:''; position:absolute; bottom:0; left:0; width:100%; height:3px; }
    .stat-card:nth-child(1)::after { background: var(--purple); box-shadow: 0 -2px 10px rgba(139,92,246,0.4); }
    .stat-card:nth-child(2)::after { background: var(--accent); box-shadow: 0 -2px 10px rgba(0,210,255,0.4); }
    .stat-card:nth-child(3)::after { background: var(--green); box-shadow: 0 -2px 10px rgba(16,185,129,0.4); }
    .stat-card:nth-child(4)::after { background: var(--orange); box-shadow: 0 -2px 10px rgba(249,115,22,0.4); }
    
    /* Trial Banner */
    .trial-banner { background: linear-gradient(135deg, rgba(249,115,22,0.1), rgba(249,115,22,0.02)); border: 1px solid var(--orange); border-radius: 10px; padding: 1rem 1.5rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; gap: 1.5rem; }
    
    /* Continue Learning Hero */
    .hero-resume { background: linear-gradient(135deg, var(--primary), #003355); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; color: white; position: relative; overflow: hidden; }
    .hero-resume::after { content: ''; position: absolute; right: -50px; bottom: -50px; width: 150px; height: 150px; background: radial-gradient(circle, var(--accent) 0%, transparent 70%); opacity: 0.2; border-radius: 50%; }
    
    /* Leaderboard & Results Layout */
    .two-col { display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; margin-bottom: 1.5rem; }
    @media (max-width: 900px) { .two-col { grid-template-columns: 1fr; } }
    
    .panel { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
    .panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .panel-title { font-size: 1rem; font-weight: 800; color: var(--text); }
    
    /* Lists - Compact */
    .list-item { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--border); }
    .list-item:last-child { border-bottom: none; }
    .list-item:hover { background: var(--bg); border-radius: 6px; border-bottom-color: transparent; }
    
    .rank-num { font-size: 1rem; font-weight: 800; color: var(--muted); width: 24px; text-align: center; }
    .rank-1 { color: var(--gold); } .rank-2 { color: #94a3b8; } .rank-3 { color: #cd7f32; }
    .lb-highlight { background: rgba(0,210,255,0.05); border: 1px solid rgba(0,210,255,0.2); border-radius: 6px; }
    
    /* Avatar inside leaderboard */
    .lb-avatar-wrap { width: 28px; height: 28px; border-radius: 50%; background: var(--bg); display: grid; place-items:center; font-size:0.7rem; font-weight:bold; color:var(--primary); border: 1px solid var(--border); }

    /* Courses Row */
    .course-row { display: flex; gap: 0.75rem; overflow-x: auto; padding-bottom: 0.5rem; scrollbar-width: thin; }
    .course-card { min-width: 220px; background: var(--card); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; transition: .2s; }
    .course-card:hover { transform: translateY(-2px); border-color: var(--accent); box-shadow: 0 4px 12px rgba(0,210,255,0.1); }
    .course-img { width: 100%; height: 100px; object-fit: cover; background: var(--bg); }
    .course-body { padding: 0.75rem; }
    
    /* Announcements */
    .ann-card { background: #eff6ff; border-left: 3px solid var(--accent); padding: 0.75rem 1rem; border-radius: 4px 8px 8px 4px; margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: flex-start; color: var(--text); }
    .ann-close { background: none; border: none; color: var(--muted); cursor: pointer; }
    .ann-close:hover { color: var(--text); }
    
    /* Quick Actions - Pill Grid */
    .qa-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 0.75rem; margin-bottom: 1.5rem; }
    .qa-btn { display: flex; flex-direction: row; align-items: center; gap: 0.5rem; background: var(--card); border: 1px solid var(--border); border-radius: 50px; padding: 0.5rem 1rem; color: var(--text); text-decoration: none; transition: .2s; font-weight: 700; font-size: 0.85rem; box-shadow: 0 2px 6px rgba(0,0,0,0.02); }
    .qa-btn:hover { background: #f8fafc; border-color: var(--accent); transform: translateY(-1px); box-shadow: 0 4px 10px rgba(0,210,255,0.1); }
    
    .qa-icon-wrap { width: 32px; height: 32px; border-radius: 50%; display: grid; place-items:center; }
    .qa-btn:nth-child(1) .qa-icon-wrap { background: rgba(16,185,129,0.1); color: var(--green); }
    .qa-btn:nth-child(2) .qa-icon-wrap { background: rgba(249,115,22,0.1); color: var(--orange); }
    .qa-btn:nth-child(3) .qa-icon-wrap { background: rgba(0,210,255,0.1); color: var(--accent); }
    .qa-btn:nth-child(4) .qa-icon-wrap { background: rgba(139,92,246,0.1); color: var(--purple); }
    
    .qa-btn .material-symbols-outlined { font-size: 1.2rem; }

  </style>"""

html = re.sub(r'/\* ── CUSTOM UI MODS FOR STUDENT DASHBOARD ── \*/.*?</style>', new_styles, html, flags=re.DOTALL)

# Update Quick Actions HTML to match new Pill design
qa_old = """      <div class="qa-grid fade-in">
        <a href="courses.html" class="qa-btn"><span class="material-symbols-outlined">library_books</span> Browse Courses</a>
        <a href="mock-exam.html" class="qa-btn"><span class="material-symbols-outlined">quiz</span> Take Mock Exam</a>
        <a href="live-class.html" class="qa-btn"><span class="material-symbols-outlined">co_present</span> Live Classes</a>
        <a href="javascript:void(0)" onclick="alert(`Coming Soon!`)" class="qa-btn" onclick="openUstadAI(true)"><span class="material-symbols-outlined">smart_toy</span> Ask Athenaeum Assistant</a>
      </div>"""
      
qa_new = """      <div class="qa-grid fade-in">
        <a href="courses.html" class="qa-btn"><div class="qa-icon-wrap"><span class="material-symbols-outlined">library_books</span></div> Browse</a>
        <a href="mock-exam.html" class="qa-btn"><div class="qa-icon-wrap"><span class="material-symbols-outlined">quiz</span></div> Mock Exam</a>
        <a href="live-class.html" class="qa-btn"><div class="qa-icon-wrap"><span class="material-symbols-outlined">co_present</span></div> Live Class</a>
        <a href="javascript:void(0)" onclick="openUstadAI(true)" class="qa-btn"><div class="qa-icon-wrap"><span class="material-symbols-outlined">smart_toy</span></div> Athenaeum Assistant</a>
      </div>"""

html = html.replace(qa_old, qa_new)

# Update Leaderboard HTML to include Avatar
lb_func_old = """          <div class="list-item ${isMe?'lb-highlight':''}">
            <div style="display:flex; align-items:center; gap:1rem;">
              <div class="rank-num rank-${idx+1}">${idx+1}</div>
              <div>
                <div style="font-weight:700">${isMe ? 'You' : p.full_name.split(' ')[0]}</div>
                <div style="font-size:0.75rem; color:var(--muted)">${lInfo.name}</div>
              </div>
            </div>
            <div style="font-weight:800; color:var(--gold)">${p.xp} XP</div>
          </div>"""
          
lb_func_new = """          <div class="list-item ${isMe?'lb-highlight':''}">
            <div style="display:flex; align-items:center; gap:0.75rem;">
              <div class="rank-num rank-${idx+1}">${idx+1}</div>
              <div class="lb-avatar-wrap">${p.full_name.substring(0,1)}</div>
              <div>
                <div style="font-weight:700; font-size:0.9rem;">${isMe ? 'You' : p.full_name.split(' ')[0]}</div>
                <div style="font-size:0.7rem; color:var(--muted)">${lInfo.name}</div>
              </div>
            </div>
            <div style="font-weight:800; color:var(--purple); font-size:0.9rem;">${p.xp} XP</div>
          </div>"""

html = html.replace(lb_func_old, lb_func_new)

with open('/Users/ali/Documents/Academy/dashboard-student.html', 'w') as f:
    f.write(html)
