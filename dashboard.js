// ── Dashboard Interactivity ─────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Sidebar Toggle
  const mobileToggle = document.getElementById('mobile-toggle');
  const sidebar = document.getElementById('sidebar');

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
          sidebar.classList.remove('open');
        }
      }
    });
  }

  // Link Child Form (Parent Dashboard)
  const linkForm = document.getElementById('link-child-form');
  if (linkForm) {
    linkForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = linkForm.querySelector('button');
      const originalText = btn.innerHTML;
      btn.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Linked Successfully!';
      btn.style.background = 'var(--clr-secondary)';
      setTimeout(() => {
        btn.innerHTML = originalText;
        btn.style.background = '';
        linkForm.reset();
        alert('Student account linked to your dashboard.');
      }, 2000);
    });
  }

  // Suggest Course Form (Student Dashboard)
  const suggestForm = document.getElementById('suggest-course-form');
  if (suggestForm) {
    suggestForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = suggestForm.querySelector('button');
      const originalText = btn.innerHTML;
      btn.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Suggestion Sent!';
      btn.style.background = 'var(--clr-secondary)';
      setTimeout(() => {
        btn.innerHTML = originalText;
        btn.style.background = '';
        suggestForm.reset();
        alert('Thank you! Your course suggestion has been submitted to the academic team.');
      }, 2000);
    });
  }

  // Set active nav item based on URL
  const navItems = document.querySelectorAll('.nav-item');
  const currentPath = window.location.pathname;
  navItems.forEach(item => {
    if (item.getAttribute('href') && currentPath.includes(item.getAttribute('href'))) {
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');
    }
  });

  // Fetch and render Supabase dashboard stats
  async function renderDashboardStats() {
    if (!window.supabaseClient || !window.AthenaeumCourses) return;
    const { data: { session } } = await window.supabaseClient.auth.getSession();
    if (!session) return;
    const userId = session.user.id;

    // Load main stats
    const stats = await window.AthenaeumCourses.getStudentDashboardStats(userId);
    if (stats) {
      const elXp = document.getElementById('dash-total-xp');
      const elCourses = document.getElementById('dash-active-courses');
      const elLessons = document.getElementById('dash-completed-lessons');
      const elUserXp = document.getElementById('dash-user-xp');
      
      if (elXp) elXp.textContent = stats.xp;
      if (elUserXp) elUserXp.textContent = `${stats.xp} XP`;
      if (elCourses) elCourses.textContent = stats.enrolledCount;
      if (elLessons) elLessons.textContent = stats.completedLessonsCount;

      // Calculate level (every 100 XP is a level)
      const level = Math.floor(stats.xp / 100) + 1;
      const currentLevelXp = stats.xp % 100;
      const xpPercent = currentLevelXp; // since it's out of 100
      
      const badgeWraps = document.querySelectorAll('.xp-level-badge');
      badgeWraps.forEach(b => b.textContent = level);
      
      const barFills = document.querySelectorAll('.xp-bar-fill');
      barFills.forEach(b => b.style.width = `${xpPercent}%`);
      
      const barLabels = document.querySelectorAll('.xp-bar-label');
      barLabels.forEach(lbl => {
        lbl.innerHTML = `<span>${stats.xp} XP · Level ${level}</span><span>100 XP → Level ${level + 1}</span>`;
      });
    }

    // Load leaderboard
    const lbList = document.getElementById('dash-lb-list');
    if (lbList) {
      const lbData = await window.AthenaeumCourses.getLeaderboard();
      if (lbData && lbData.length > 0) {
        lbList.innerHTML = ''; // clear loading state
        lbData.forEach((user, index) => {
          const rank = index + 1;
          const isMe = user.id === userId;
          const nameStr = isMe ? `<span class="user-name-display">${user.full_name}</span> <span style="font-size:.65rem;color:var(--clr-secondary);font-weight:700;">YOU</span>` : user.full_name;
          const avatarStr = user.full_name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
          
          let trendHtml = '';
          if (rank === 1) trendHtml = `<div class="lb-trend up"><span class="material-symbols-outlined">star</span></div>`;
          else trendHtml = `<div class="lb-trend same"><span class="material-symbols-outlined">remove</span></div>`;

          lbList.innerHTML += `
            <li class="lb-item ${isMe ? 'me' : ''}">
              <div class="lb-rank">${rank}</div>
              <div class="lb-avatar" style="background:var(--clr-accent);color:var(--clr-primary-dark);">${avatarStr}</div>
              <div class="lb-info">
                <div class="lb-name">${nameStr}</div>
                <div class="lb-course">Student</div>
              </div>
              <div class="lb-pts">${user.xp || 0} XP</div>
              ${trendHtml}
            </li>
          `;
        });
      }
    }

    // Load active announcements
    const container = document.getElementById('announcements-container');
    if (container) {
      // Get user plan_type
      const { data: profile } = await window.supabaseClient.from('profiles').select('plan_type').eq('id', userId).single();
      const planType = profile?.plan_type || 'trial';
      
      const { data: announcements } = await window.supabaseClient.from('announcements')
        .select('*')
        .eq('is_active', true)
        .order('created_at', { ascending: false });
        
      if (announcements && announcements.length > 0) {
        const relevant = announcements.filter(a => a.target === 'all' || a.target === planType);
        if (relevant.length > 0) {
          container.innerHTML = relevant.map(a => `
            <div class="card" style="background:linear-gradient(135deg, var(--clr-primary-dark), #0f172a); border-left:4px solid var(--clr-accent); margin-bottom:1.5rem; display:flex; gap:1rem; align-items:center;">
              <div style="font-size:2rem; background:rgba(255,255,255,0.1); width:48px; height:48px; border-radius:50%; display:flex; align-items:center; justify-content:center;">📢</div>
              <div>
                <h3 style="margin:0 0 0.25rem 0; color:white; font-size:1.1rem;">${a.title}</h3>
                <p style="margin:0; color:var(--muted); font-size:0.9rem;">${a.message}</p>
              </div>
            </div>
          `).join('');
        }
      }
    }
  }

  // Trigger rendering if we are on student dashboard
  if (window.location.pathname.includes('dashboard-student.html')) {
    renderDashboardStats();
  }
});
