const fs = require("fs");
let html = fs.readFileSync("admin.html", "utf8");

// Update adminLogout
const logoutRegex = /async function adminLogout\(\) \{[\s\S]*?\n\}/;
const newLogout = `async function adminLogout() {
  await window.supabaseClient.auth.signOut();
  window.location.href = "index.html";
}`;
html = html.replace(logoutRegex, newLogout);

// Update auto-detect session
const sessionRegex = /window\.addEventListener\('DOMContentLoaded', async \(\) => \{[\s\S]*?\}\);/;
const newSession = `window.addEventListener('DOMContentLoaded', async () => {
  const { data: { session } } = await window.supabaseClient.auth.getSession();
  if (!session || session?.user?.email !== ADMIN_EMAIL) {
    window.location.href = 'index.html';
    return;
  }
  document.getElementById('sidebar-email').textContent = session.user.email;
  document.getElementById('admin-app').style.display = 'block';
  loadDashboardStats();
  loadStudents();
  loadTeachers();
  loadAnnouncements();
  showToast('Auto-logged in as Admin 👋', 'success');
});`;
html = html.replace(sessionRegex, newSession);

fs.writeFileSync("admin.html", html);
