// Frontend Route Guard using Supabase
document.addEventListener('DOMContentLoaded', async () => {
  // Ensure supabaseClient is loaded
  if (!window.supabaseClient) {
    console.error('Supabase client not loaded. Guard failed.');
    window.location.href = 'auth.html';
    return;
  }

  // Get current session
  const { data: { session }, error } = await window.supabaseClient.auth.getSession();

  // If no session exists, redirect instantly
  if (!session || error) {
    // Optional: Keep trial params if checking URL, but generally redirect to auth
    console.warn('Unauthorized access attempt. Redirecting to auth...');
    window.location.href = 'auth.html';
  } // <-- Added missing closing brace here

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
