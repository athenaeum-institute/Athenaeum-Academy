// Frontend Route Guard using Supabase
document.addEventListener('DOMContentLoaded', async () => {
  // Ensure supabaseClient is loaded
  if (!window.supabaseClient) {
    console.error('Supabase client not loaded. Guard failed.');
    window.location.href = 'auth.html';
    return;
  }

  // Get current session
  let { data: { session }, error } = await window.supabaseClient.auth.getSession();

  // Handle OAuth redirect delay (sometimes getSession is faster than URL parsing)
  if (!session && window.location.hash.includes('access_token')) {
    await new Promise((resolve) => {
      const { data: { subscription } } = window.supabaseClient.auth.onAuthStateChange((event, newSession) => {
        if (event === 'SIGNED_IN' || newSession) {
          session = newSession;
          subscription.unsubscribe();
          resolve();
        }
      });
      // Fallback timeout just in case
      setTimeout(() => resolve(), 2000);
    });
  }

  // If no session exists, redirect instantly
  if (!session || error) {
    if (window.location.hash.includes('error_description=')) {
        alert("Google Login Error: Please check Supabase Redirect URLs configuration.");
    }
    console.warn('Unauthorized access attempt. Redirecting to auth...');
    window.location.href = 'auth.html';
    return;
  }

  // Session exists. Check user role
  const user = session.user;
  
  // Explicitly check for master admin email
  let role = (user.user_metadata?.role || 'student').toLowerCase();
  if (user.email === 'athenaeum.institute@gmail.com') {
    role = 'admin';
  }
  
  const fullName = user.user_metadata?.full_name || user.email.split('@')[0];
  const currentPath = window.location.pathname.toLowerCase();
  
  // Route enforcement
  if (role === 'admin' && !currentPath.includes('admin.html')) {
    window.location.href = 'admin.html';
    return;
  }
  if (role === 'student' && currentPath.includes('admin.html')) {
    window.location.href = 'dashboard-student.html';
    return;
  }
  if (role === 'teacher' && !currentPath.includes('teacher')) {
    // If teacher tries to access admin, send them to teacher dashboard (assuming you have one)
    if (currentPath.includes('admin.html')) {
        window.location.href = 'dashboard-teacher.html';
        return;
    }
  }
  if (role === 'parent' && !currentPath.includes('parent')) {
    if (currentPath.includes('admin.html')) {
        window.location.href = 'dashboard-parent.html';
        return;
    }
  }

  // Inject dynamic data for allowed page
  console.log('User authenticated:', user.email, 'Role:', role);

  const initials = fullName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();

  // Update DOM elements on page load
  document.querySelectorAll('.user-name-display').forEach(el => {
    el.textContent = fullName;
  });

  document.querySelectorAll('.user-initials-display').forEach(el => {
    el.textContent = initials;
  });
});
