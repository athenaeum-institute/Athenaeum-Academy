// ============================================================
// Athenaeum — Authentication State Manager
// ============================================================

/**
 * Get current authenticated user session
 */
async function getCurrentUser() {
  try {
    const { data: { session }, error } = await window.supabaseClient.auth.getSession();
    if (error) throw error;
    return session?.user || null;
  } catch (error) {
    console.error("Error getting session:", error);
    return null;
  }
}

/**
 * Fetch user profile (name, plan_type)
 */
async function getUserProfile(userId) {
  try {
    const { data, error } = await window.supabaseClient
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .maybeSingle();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error("Error fetching profile:", error);
    return null;
  }
}

/**
 * Redirect based on user role
 */
function redirectBasedOnRole(role) {
  if (role === 'Admin') return 'admin.html';
  if (role === 'Teacher') return 'dashboard-teacher.html';
  if (role === 'Parent') return 'dashboard-parent.html';
  return 'dashboard-student.html';
}

/**
 * Check if the user is logging in for the very first time
 */
async function isFirstLogin(userId) {
  const profile = await getUserProfile(userId);
  if (!profile) return false;
  // If last_login_date is null or matches created_at (roughly), it's first login
  // Alternatively, we can rely on streak_days === 0 and last_login_date being today.
  // A simpler way: we set last_login_date on registration. If we haven't set it yet, it's first login.
  // For safety, let's check localStorage.
  const key = `first_login_${userId}`;
  if (localStorage.getItem(key)) return false;
  localStorage.setItem(key, 'false');
  return true;
}

/**
 * Check Trial Status
 */
function checkTrialStatus(profile) {
  if (!profile || profile.plan_type !== 'trial') return { active: false, daysLeft: 0 };
  
  let endDate;
  if (profile.trial_end_date) {
    endDate = new Date(profile.trial_end_date);
  } else if (profile.created_at) {
    endDate = new Date(profile.created_at);
    endDate.setTime(endDate.getTime() + (3 * 24 * 60 * 60 * 1000)); // Exactly 72 hours
  } else {
    // Fallback if neither exists
    endDate = new Date();
    endDate.setDate(endDate.getDate() + 3);
  }
  
  const now = new Date();
  const diffTime = endDate - now;
  const daysLeft = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return { active: daysLeft > 0, daysLeft: Math.max(0, daysLeft) };
}

/**
 * Handle Logout
 */
window.handleLogout = async function() {
  try {
    const user = await getCurrentUser();
    if(user) {
      sessionStorage.removeItem(`welcome_shown_${user.id}`);
      sessionStorage.removeItem(`session_started_${user.id}`);
    }
    
    // Change button text to show progress
    const logoutBtns = document.querySelectorAll("button[onclick*=\"handleLogout\"]");
    logoutBtns.forEach(btn => {
      btn.innerHTML = "<span class=\"material-symbols-outlined spinner\" style=\"animation: spin 1s linear infinite;\">sync</span> Logging out...";
      btn.style.pointerEvents = "none";
    });

    await window.supabaseClient.auth.signOut();
    
    // Hard clear storage
    sessionStorage.clear();
    localStorage.removeItem("supabase.auth.token");
    localStorage.removeItem("welcome_shown");
    
    // Toast notification
    const toast = document.createElement('div');
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.background = '#25D366';
    toast.style.color = '#fff';
    toast.style.padding = '12px 24px';
    toast.style.borderRadius = '8px';
    toast.style.zIndex = '10000';
    toast.innerText = 'You have been logged out successfully. See you soon! 👋';
    document.body.appendChild(toast);
    
    setTimeout(() => {
      window.location.href = 'index.html';
    }, 1500);
    
  } catch (error) {
    console.error("Error logging out:", error);
    alert("Logout failed. Please try again.");
    window.location.href = 'index.html';
  }
}

/**
 * Update Navbar based on Auth State
 */
async function updateNavbar() {
  const user = await getCurrentUser();
  const navActions = document.querySelector('.nav-actions');
  const mobileActions = document.querySelector('.mobile-actions');
  
  if (!navActions) return;

  if (user) {
    const profile = await getUserProfile(user.id);
    const firstName = profile?.full_name?.split(' ')[0] || 'Student';
    const initial = firstName.charAt(0).toUpperCase();
    const role = profile?.role || 'Student';
    const planType = profile?.plan_type || 'trial';
    
    const dashboardUrl = redirectBasedOnRole(role);
    const badgeText = planType === 'paid' ? '✨ Premium Member' : '✨ Free Trial';

    // Desktop Nav Update
    const loginBtn = document.getElementById('btn-login');
    const startLearningBtn = document.getElementById('btn-start-learning');
    
    if (loginBtn) loginBtn.style.display = 'none';
    if (startLearningBtn) startLearningBtn.style.display = 'none';

    // Create User Dropdown
    if (!document.getElementById('nav-user-wrapper')) {
      const userWrapper = document.createElement('div');
      userWrapper.id = 'nav-user-wrapper';
      userWrapper.className = 'nav-user-wrapper';
      userWrapper.innerHTML = `
        <button class="nav-user-btn" onclick="document.getElementById('nav-user-dropdown').classList.toggle('show')">
          <div class="nav-user-avatar" style="transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">${initial}</div>
          ${firstName} <span class="material-symbols-outlined" style="font-size:18px">expand_more</span>
        </button>
        <div id="nav-user-dropdown" class="nav-user-dropdown">
          <div style="padding: 10px 12px; display:flex; flex-direction:column; gap:2px;">
            <strong style="color: var(--clr-primary); font-size: 14px;">👤 ${profile?.full_name || 'Student'}</strong>
            <span style="font-size: 11px; color: var(--clr-on-surface-var);">${badgeText}</span>
          </div>
          <hr>
          <a href="${dashboardUrl}">
            <span class="material-symbols-outlined">space_dashboard</span> My Dashboard
          </a>
          <a href="courses.html">
            <span class="material-symbols-outlined">library_books</span> My Courses
          </a>
          <a href="#" onclick="if(window.toggleUstadAI) toggleUstadAI(); return false;">
            <span class="material-symbols-outlined">smart_toy</span> Ustad AI
          </a>
          <a href="#">
            <span class="material-symbols-outlined">settings</span> Settings
          </a>
          <hr>
          <button onclick="handleLogout()">
            <span class="material-symbols-outlined">logout</span> Logout
          </button>
        </div>
      `;
      navActions.appendChild(userWrapper);
      
      // Close dropdown when clicking outside
      document.addEventListener('click', (e) => {
        if (!userWrapper.contains(e.target)) {
          const dropdown = document.getElementById('nav-user-dropdown');
          if(dropdown) dropdown.classList.remove('show');
        }
      });
    }

    // Mobile Nav Update
    if (mobileActions) {
      mobileActions.innerHTML = `
        <a href="${dashboardUrl}" class="btn btn-primary full-width">My Dashboard</a>
        <button onclick="handleLogout()" class="btn btn-ghost full-width" style="margin-top: 10px;">Logout</button>
      `;
    }

  } else {
    // Ensure default state is visible
    const loginBtn = document.getElementById('btn-login');
    const startLearningBtn = document.getElementById('btn-start-learning');
    if (loginBtn) loginBtn.style.display = 'inline-flex';
    if (startLearningBtn) startLearningBtn.style.display = 'inline-flex';
    
    const userWrapper = document.getElementById('nav-user-wrapper');
    if (userWrapper) userWrapper.remove();
  }
}

/**
 * Update Hero Section based on Auth State
 */
async function updateHeroSection() {
  const heroCopy = document.querySelector('.hero-copy');
  if (!heroCopy) return; // Only run on pages with hero (like index.html)

  const user = await getCurrentUser();
  if (!user) return; // Keep default if not logged in
  
  const profile = await getUserProfile(user.id);
  const firstName = profile?.full_name?.split(' ')[0] || 'Student';
  const role = profile?.role || 'Student';
  
  const dashboardUrl = redirectBasedOnRole(role);

  const titleEl = document.querySelector('.hero-title');
  const ctas = document.querySelector('.hero-ctas');

  if (titleEl) {
    // Smooth transition
    titleEl.style.opacity = '0';
    setTimeout(() => {
      titleEl.innerHTML = `Welcome back, <span class="accent-text">${firstName}!</span> 👋<br><span style="font-size: 24px; color: var(--clr-on-surface-var); font-weight: 500; display:block; margin-top:10px;">Ready to continue your learning journey?</span>`;
      titleEl.style.transition = 'opacity 0.5s ease';
      titleEl.style.opacity = '1';
    }, 300);
  }

  if (ctas) {
    ctas.style.opacity = '0';
    setTimeout(() => {
      ctas.innerHTML = `
        <a href="${dashboardUrl}" class="btn btn-primary btn-lg">
          Go to Dashboard <span class="material-symbols-outlined">rocket_launch</span>
        </a>
        <a href="courses.html" class="btn btn-outline btn-lg">
          Browse Courses
        </a>
      `;
      ctas.style.transition = 'opacity 0.5s ease';
      ctas.style.opacity = '1';
    }, 300);
  }
}

/**
 * Show Premium Welcome Overlay once per session
 */
async function showWelcomeMessage() {
  const user = await getCurrentUser();
  if (!user) return;
  
  const sessionKey = `welcome_shown_${user.id}`;
  if (sessionStorage.getItem(sessionKey)) return; // Already shown this session
  
  const profile = await getUserProfile(user.id);
  const firstName = profile?.full_name?.split(' ')[0] || 'Student';
  const planType = profile?.plan_type || 'trial';
  const role = profile?.role || 'Student';
  const streak = profile?.streak_days || 1;
  const trialStatus = checkTrialStatus(profile);
  
  const dashboardUrl = redirectBasedOnRole(role);

  const badgeText = planType === 'paid' ? '✨ Premium Member' : `✨ Free Trial: ${trialStatus.daysLeft} days left`;

  // Build the modal
  const modal = document.createElement('div');
  modal.className = 'premium-welcome-modal';
  modal.innerHTML = `
    <button class="welcome-close-btn" onclick="this.parentElement.classList.remove('show')">✕</button>
    <div class="welcome-header">
      <div class="welcome-emoji">👋</div>
      <div class="welcome-content">
        <h4>Welcome back, ${firstName}!</h4>
      </div>
    </div>
    <div class="welcome-footer">
      <div style="display:flex; flex-direction:column; gap:4px; margin-bottom: 8px;">
        <span style="font-size: 13px; font-weight: 700; color: #ff5722;">🔥 ${streak} Day Streak!</span>
        <span class="welcome-badge">${badgeText}</span>
      </div>
      <a href="${dashboardUrl}" class="welcome-btn">Go to Dashboard →</a>
    </div>
  `;

  document.body.appendChild(modal);

  // Trigger animation
  setTimeout(() => {
    modal.classList.add('show');
  }, 500);

  // Auto dismiss
  setTimeout(() => {
    const m = document.querySelector('.premium-welcome-modal');
    if (m) m.classList.remove('show');
    setTimeout(() => { if(m) m.remove() }, 500);
  }, 5500);

  // Mark as shown
  sessionStorage.setItem(sessionKey, 'true');
}

// Global Init on Page Load
document.addEventListener('DOMContentLoaded', () => {
  if (window.supabaseClient) {
    updateNavbar();
    
    // Only run these on index.html (detect by hero presence)
    if (document.getElementById('hero')) {
      updateHeroSection();
      showWelcomeMessage();
    }
  }
});
