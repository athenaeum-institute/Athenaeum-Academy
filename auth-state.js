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
      .select('full_name, plan_type, role')
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
 * Handle Logout
 */
window.handleLogout = async function() {
  try {
    const user = await getCurrentUser();
    if(user) {
      sessionStorage.removeItem(`welcome_shown_${user.id}`);
    }
    await window.supabaseClient.auth.signOut();
    
    // Toast notification
    const toast = document.createElement('div');
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.left = '50%';
    toast.style.transform = 'translateX(-50%)';
    toast.style.background = '#333';
    toast.style.color = '#fff';
    toast.style.padding = '10px 20px';
    toast.style.borderRadius = '50px';
    toast.style.zIndex = '10000';
    toast.innerText = 'Logged out successfully 👋';
    document.body.appendChild(toast);
    
    setTimeout(() => {
      window.location.href = 'index.html';
    }, 1000);
    
  } catch (error) {
    console.error("Logout error:", error);
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
    
    // Determine Dashboard URL
    let dashboardUrl = 'dashboard-student.html';
    if (role === 'Admin') dashboardUrl = 'admin.html';
    else if (role === 'Teacher') dashboardUrl = 'dashboard-teacher.html';
    else if (role === 'Parent') dashboardUrl = 'dashboard-parent.html';

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
          <div class="nav-user-avatar">${initial}</div>
          ${firstName} <span class="material-symbols-outlined" style="font-size:18px">expand_more</span>
        </button>
        <div id="nav-user-dropdown" class="nav-user-dropdown">
          <a href="${dashboardUrl}">
            <span class="material-symbols-outlined">space_dashboard</span> My Dashboard
          </a>
          <a href="#">
            <span class="material-symbols-outlined">person</span> My Profile
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
      // Append to the right side of nav-actions (before or after icons? The user wants replace Login/Register)
      // nav-icons are there, we append to the end.
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
  
  let dashboardUrl = 'dashboard-student.html';
  if (role === 'Admin') dashboardUrl = 'admin.html';
  else if (role === 'Teacher') dashboardUrl = 'dashboard-teacher.html';
  else if (role === 'Parent') dashboardUrl = 'dashboard-parent.html';

  const titleEl = document.querySelector('.hero-title');
  const ctas = document.querySelector('.hero-ctas');

  if (titleEl) {
    // Smooth transition
    titleEl.style.opacity = '0';
    setTimeout(() => {
      titleEl.innerHTML = `Welcome back, <span class="accent-text">${firstName}!</span> 👋<br><span style="font-size: 24px; color: var(--clr-on-surface-var); font-weight: 500; display:block; margin-top:10px;">Ready to continue your journey?</span>`;
      titleEl.style.transition = 'opacity 0.5s ease';
      titleEl.style.opacity = '1';
    }, 300);
  }

  if (ctas) {
    ctas.style.opacity = '0';
    setTimeout(() => {
      ctas.innerHTML = `
        <a href="${dashboardUrl}" class="btn btn-primary btn-lg">
          Go to Dashboard <span class="material-symbols-outlined">arrow_forward</span>
        </a>
        <a href="courses.html" class="btn btn-outline btn-lg">
          Explore Courses
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
  
  let dashboardUrl = 'dashboard-student.html';
  if (role === 'Admin') dashboardUrl = 'admin.html';
  else if (role === 'Teacher') dashboardUrl = 'dashboard-teacher.html';
  else if (role === 'Parent') dashboardUrl = 'dashboard-parent.html';

  // Determine time of day
  const hour = new Date().getHours();
  let emoji, greeting, subtitle;
  
  if (hour >= 5 && hour < 12) {
    emoji = '🌅';
    greeting = `Subah Bakhair, ${firstName}!`;
    subtitle = `Aaj ka din productive banao.<br>Tumhara Ustad AI ready hai! ✨`;
  } else if (hour >= 12 && hour < 17) {
    emoji = '☀️';
    greeting = `Assalam o Alaikum, ${firstName}!`;
    subtitle = `Chalo aaj kuch naya seekhte hain.<br>Tumhari journey continue karo! 🚀`;
  } else if (hour >= 17 && hour < 21) {
    emoji = '🌙';
    greeting = `Shaam Bakhair, ${firstName}!`;
    subtitle = `Aaj bhi kuch seekhne ka waqt hai.<br>Ustad AI tumhara intezaar kar raha hai! 💫`;
  } else {
    emoji = '⭐';
    greeting = `Good Night, ${firstName}!`;
    subtitle = `Kal subah fresh start karo.<br>Tumhari progress save hai! 🎯`;
  }

  const badgeText = planType === 'paid' ? '✨ Premium Member' : '🎓 Free Trial Active';

  // Build the modal
  const modal = document.createElement('div');
  modal.className = 'premium-welcome-modal';
  modal.innerHTML = `
    <button class="welcome-close-btn" onclick="this.parentElement.classList.remove('show')">✕</button>
    <div class="welcome-header">
      <div class="welcome-emoji">${emoji}</div>
      <div class="welcome-content">
        <h4>${greeting}</h4>
        <p>${subtitle}</p>
      </div>
    </div>
    <div class="welcome-footer">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span class="welcome-badge">${badgeText}</span>
        <span style="font-size: 11px; font-weight: 700; color: #ff5722;">🔥 1 Day Streak!</span>
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
  }, 6000);

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
