// ─────────────────────────────────────────────────────────────
// Shared Announcements Logic
// Automatically imported in all dashboard pages.
// ─────────────────────────────────────────────────────────────

class AthenaeumAnnouncements {
  constructor() {
    this.client = window.supabaseClient;
    this.userId = null;
    this.userRole = 'student';
    this.planType = 'trial';
    this.enrolledCourseIds = [];
    this.activeAnnouncements = [];
    
    // Default container IDs
    this.bannerContainerId = 'global-announcements';
    this.bellContainerId = 'notification-bell';
  }

  async init() {
    try {
      const { data: { session } } = await this.client.auth.getSession();
      if (!session) return; // not logged in

      this.userId = session.user.id;

      // Fetch Profile for role/plan
      const { data: profile } = await this.client.from('profiles').select('role, plan_type').eq('id', this.userId).single();
      if (profile) {
        this.userRole = profile.role || 'student';
        this.planType = profile.plan_type || 'trial';
      }

      // If student, fetch enrolled courses
      if (this.userRole === 'student') {
        const { data: enrollments } = await this.client.from('enrollments').select('course_id').eq('student_id', this.userId);
        if (enrollments) {
          this.enrolledCourseIds = enrollments.map(e => e.course_id);
        }
      }

      // Initial Fetch
      await this.fetchAnnouncements();
      
      // Setup Realtime
      this.initRealtime();

    } catch (e) {
      console.error("Failed to initialize announcements:", e);
    }
  }

  getDismissedIds() {
    if (!this.userId) return [];
    try {
      const stored = localStorage.getItem(`dismissed_announcements_${this.userId}`);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  dismissAnnouncement(id) {
    if (!this.userId) return;
    const dismissed = this.getDismissedIds();
    if (!dismissed.includes(id)) {
      dismissed.push(id);
      localStorage.setItem(`dismissed_announcements_${this.userId}`, JSON.stringify(dismissed));
    }
    // Re-render
    this.fetchAnnouncements(); // re-filter and render
  }

  markAllRead() {
    if (!this.userId) return;
    const dismissed = this.getDismissedIds();
    this.activeAnnouncements.forEach(a => {
      if (!a.is_pinned && !dismissed.includes(a.id)) {
        dismissed.push(a.id);
      }
    });
    localStorage.setItem(`dismissed_announcements_${this.userId}`, JSON.stringify(dismissed));
    this.fetchAnnouncements();
  }

  async fetchAnnouncements() {
    // Determine target string
    let targetMatch = 'all';
    if (this.userRole === 'parent') targetMatch = 'parents';
    if (this.userRole === 'teacher') targetMatch = 'teachers';
    if (this.userRole === 'student' && this.planType === 'paid') targetMatch = 'paid';
    if (this.userRole === 'student' && this.planType === 'trial') targetMatch = 'trial';

    const now = new Date().toISOString();

    let query = this.client.from('announcements')
      .select('*')
      .eq('is_active', true)
      .or(`expires_at.is.null,expires_at.gt.${now}`)
      .order('is_pinned', { ascending: false })
      .order('created_at', { ascending: false });

    const { data, error } = await query;
    if (error) {
      console.error(error);
      return;
    }

    // Filter locally based on target and course_id
    let filtered = data.filter(a => {
      // Check target
      const targetValid = (a.target === 'all' || a.target === targetMatch || (this.userRole === 'admin'));
      
      // Check course_id (if it has a course_id, only enrolled students or teachers/admins see it)
      let courseValid = true;
      if (a.course_id) {
        if (this.userRole === 'student') {
          courseValid = this.enrolledCourseIds.includes(a.course_id);
        }
        // Teacher/Admin can see all course announcements, but usually we filter in UI
      }

      return targetValid && courseValid;
    });

    this.activeAnnouncements = filtered;
    this.renderAnnouncements();
    this.renderNotificationBell();
  }

  renderAnnouncements() {
    const container = document.getElementById(this.bannerContainerId);
    if (!container) return;

    const dismissed = this.getDismissedIds();
    
    // Only show ones not dismissed, or pinned (pinned can never be dismissed visually from banners)
    let visible = this.activeAnnouncements.filter(a => a.is_pinned || !dismissed.includes(a.id));
    
    // If more than 3, just take top 3
    const toShow = visible.slice(0, 3);
    const extraCount = visible.length - 3;

    container.innerHTML = toShow.map(a => this.buildBannerHtml(a)).join('');

    if (extraCount > 0) {
      container.innerHTML += `
        <div style="text-align:center; padding:0.5rem; color:var(--muted); font-size:0.85rem; cursor:pointer;" onclick="document.getElementById('notification-bell-btn').click()">
          + ${extraCount} more announcements (Check Notifications)
        </div>
      `;
    }
  }

  buildBannerHtml(a) {
    let bg = '#005088'; // info
    let icon = 'info';
    let pulseCls = '';
    
    if (a.type === 'success') { bg = '#3fb950'; icon = 'check_circle'; }
    if (a.type === 'warning') { bg = '#d29922'; icon = 'warning'; }
    if (a.type === 'urgent') { bg = '#f85149'; icon = 'error'; pulseCls = 'urgent-pulse'; }

    const timeAgo = this.timeSince(new Date(a.created_at));

    return `
      <div id="ann-banner-${a.id}" class="ann-banner-card fade-in ${pulseCls}" style="background:${bg}; color:#fff; padding:1rem 1.5rem; border-radius:8px; margin-bottom:1rem; display:flex; justify-content:space-between; align-items:flex-start; box-shadow:0 5px 15px rgba(0,0,0,0.2);">
        <div style="display:flex; gap:1rem;">
          <span class="material-symbols-outlined" style="font-size:1.5rem">${icon}</span>
          <div>
            <strong style="display:block; margin-bottom:0.25rem">${a.title}</strong>
            <span style="font-size:0.9rem">${a.message}</span>
            <div style="font-size:0.75rem; margin-top:0.5rem; opacity:0.8;">${timeAgo}</div>
          </div>
        </div>
        ${a.is_pinned ? 
          `<span class="material-symbols-outlined" style="opacity:0.8" title="Pinned">push_pin</span>` : 
          `<button onclick="window.AthenaeumAnnManager.dismissAnnouncement('${a.id}')" style="background:none;border:none;color:#fff;cursor:pointer;opacity:0.8"><span class="material-symbols-outlined">close</span></button>`
        }
      </div>
    `;
  }

  renderNotificationBell() {
    const container = document.getElementById(this.bellContainerId);
    if (!container) return;

    const dismissed = this.getDismissedIds();
    // Unread count is active announcements that are not dismissed (ignoring pinned rule for the counter itself)
    const unread = this.activeAnnouncements.filter(a => !dismissed.includes(a.id)).length;

    let badgeHtml = '';
    if (unread > 0) {
      badgeHtml = `<div style="position:absolute; top:-2px; right:-2px; background:#f85149; color:white; font-size:0.6rem; font-weight:800; border-radius:50%; width:16px; height:16px; display:flex; align-items:center; justify-content:center; border:2px solid var(--card)">${unread}</div>`;
    }

    // Dropdown list
    let listHtml = '';
    if (this.activeAnnouncements.length === 0) {
      listHtml = `<div style="padding:1rem; text-align:center; color:var(--muted); font-size:0.9rem">No new notifications.</div>`;
    } else {
      listHtml = this.activeAnnouncements.map(a => {
        const isRead = dismissed.includes(a.id);
        return `
          <div style="padding:1rem; border-bottom:1px solid var(--border); background:${isRead ? 'transparent' : 'rgba(0,210,255,0.05)'}; cursor:pointer;" onclick="document.getElementById('ann-banner-${a.id}')?.scrollIntoView({behavior:'smooth', block:'center'})">
            <strong style="display:block; font-size:0.9rem; margin-bottom:0.25rem">${a.title}</strong>
            <div style="font-size:0.8rem; color:var(--muted)">${this.timeSince(new Date(a.created_at))}</div>
          </div>
        `;
      }).join('');
    }

    container.innerHTML = `
      <div style="position:relative;">
        <button class="icon-btn" id="notification-bell-btn" aria-label="Notifications" onclick="document.getElementById('notif-dropdown').classList.toggle('show')">
          <span class="material-symbols-outlined">notifications</span>
          ${badgeHtml}
        </button>
        <div id="notif-dropdown" style="display:none; position:absolute; right:0; top:40px; width:300px; background:var(--card); border:1px solid var(--border); border-radius:12px; box-shadow:0 10px 40px rgba(0,0,0,0.8); z-index:1000; overflow:hidden;">
          <div style="display:flex; justify-content:space-between; align-items:center; padding:1rem; border-bottom:1px solid var(--border); background:rgba(0,0,0,0.2);">
            <strong style="font-family:'Merriweather'">Notifications</strong>
            ${unread > 0 ? `<button style="background:none;border:none;color:var(--accent);font-size:0.8rem;cursor:pointer;font-weight:700" onclick="window.AthenaeumAnnManager.markAllRead()">Mark all read</button>` : ''}
          </div>
          <div style="max-height:350px; overflow-y:auto;">
            ${listHtml}
          </div>
        </div>
      </div>
    `;

    // Global click listener to close dropdown
    document.addEventListener('click', (e) => {
      const btn = document.getElementById('notification-bell-btn');
      const dd = document.getElementById('notif-dropdown');
      if (btn && dd && !btn.contains(e.target) && !dd.contains(e.target)) {
        dd.classList.remove('show');
        dd.style.display = 'none';
      } else if (btn && btn.contains(e.target)) {
        dd.style.display = dd.style.display === 'none' ? 'block' : 'none';
      }
    });
  }

  initRealtime() {
    this.client.channel('public:announcements')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'announcements' }, payload => {
        // Handle new/updated announcements
        console.log('Realtime Announcement update received!', payload);
        this.fetchAnnouncements(); // re-fetch and re-render
        
        // Show toast for new
        if (payload.eventType === 'INSERT') {
          this.showToast(`New Announcement: ${payload.new.title}`);
        }
      })
      .subscribe();
  }

  showToast(msg) {
    let tc = document.getElementById('toast-container');
    if (!tc) {
      tc = document.createElement('div');
      tc.id = 'toast-container';
      tc.style.cssText = "position:fixed; bottom:20px; right:20px; z-index:9999; display:flex; flex-direction:column; gap:0.5rem;";
      document.body.appendChild(tc);
    }
    const t = document.createElement('div');
    t.style.cssText = "background:var(--card, #161b22); border:1px solid var(--accent, #00D2FF); padding:1rem 1.5rem; border-radius:8px; color:#fff; font-weight:600; box-shadow:0 5px 15px rgba(0,0,0,0.5); animation:slideIn 0.3s forwards;";
    t.innerText = msg;
    tc.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; setTimeout(()=>t.remove(), 300); }, 5000);
  }

  timeSince(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + " years ago";
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + " months ago";
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + " days ago";
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + " hours ago";
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + " mins ago";
    return Math.floor(seconds) + " seconds ago";
  }
}

// Global CSS for pulse animation
const style = document.createElement('style');
style.innerHTML = `
  @keyframes pulseUrgent { 0% { box-shadow: 0 0 0 0 rgba(248,81,73,0.7); } 70% { box-shadow: 0 0 0 10px rgba(248,81,73,0); } 100% { box-shadow: 0 0 0 0 rgba(248,81,73,0); } }
  .urgent-pulse { animation: pulseUrgent 2s infinite; }
`;
document.head.appendChild(style);

window.AthenaeumAnnManager = new AthenaeumAnnouncements();
window.addEventListener('load', () => window.AthenaeumAnnManager.init());
