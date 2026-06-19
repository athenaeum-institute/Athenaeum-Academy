import os

main_js_path = 'main.js'

with open(main_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

if '// ── Search overlay' not in content:
    search_js = '''
// ── Search overlay & Instant Search ─────────────────────────
const btnSearch = document.getElementById('btn-search');
const searchOverlay = document.getElementById('search-overlay');
const globalSearchInput = document.getElementById('global-search-input');

if (btnSearch && searchOverlay) {
  // Create a container for results
  const resultsContainer = document.createElement('div');
  resultsContainer.id = 'search-results-container';
  resultsContainer.style.cssText = 'max-width: 800px; margin: 10px auto 0 auto; display: none; background: var(--clr-surface); border: 1px solid var(--clr-border); border-radius: 8px; box-shadow: var(--shadow-md); max-height: 400px; overflow-y: auto;';
  searchOverlay.appendChild(resultsContainer);

  let allCoursesForSearch = null;

  btnSearch.addEventListener('click', async () => {
    const isShowing = searchOverlay.style.display === 'block';
    searchOverlay.style.display = isShowing ? 'none' : 'block';
    
    if (!isShowing) {
      if (globalSearchInput) {
        globalSearchInput.focus();
        globalSearchInput.value = '';
      }
      
      // Fetch courses once
      if (!allCoursesForSearch && window.AthenaeumCourses) {
        try {
          const res = await window.AthenaeumCourses.fetchAllCourses();
          if (res) {
            allCoursesForSearch = res;
          }
        } catch(e) {
          console.error("Failed to load courses for search", e);
        }
      }
    } else {
      resultsContainer.style.display = 'none';
      if (globalSearchInput) globalSearchInput.value = '';
    }
  });

  if (globalSearchInput) {
    globalSearchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      
      if (!q || !allCoursesForSearch) {
        resultsContainer.style.display = 'none';
        return;
      }
      
      const filtered = allCoursesForSearch.filter(c => 
        (c.title && c.title.toLowerCase().includes(q)) || 
        (c.subject && c.subject.toLowerCase().includes(q)) ||
        (c.category && c.category.toLowerCase().includes(q))
      );
      
      resultsContainer.style.display = 'block';
      if (filtered.length > 0) {
        resultsContainer.innerHTML = filtered.map(c => `
          <a href="course-details.html?id=${c.id}" style="display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-bottom: 1px solid var(--clr-surface-high); text-decoration: none; color: inherit; transition: background 0.2s;">
            <img src="${c.thumbnail_url || 'https://via.placeholder.com/60x40'}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;">
            <div>
              <div style="font-weight: 600; font-size: 14px; color: var(--clr-primary);">${c.title}</div>
              <div style="font-size: 12px; color: var(--clr-on-surface-var); margin-top: 2px;">${c.subject || c.category}</div>
            </div>
          </a>
        `).join('');
      } else {
        resultsContainer.innerHTML = '<div style="padding: 16px; text-align: center; color: var(--clr-on-surface-var);">No courses found matching your search.</div>';
      }
    });

    // Handle enter key
    globalSearchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        executeGlobalSearch();
      }
    });
  }
}

function executeGlobalSearch() {
  const q = document.getElementById('global-search-input')?.value.trim() || '';
  if (!q) return;
  // if we are already on courses.html, redirect there anyway with parameter
  window.location.href = `courses.html?search=${encodeURIComponent(q)}`;
}
'''
    with open(main_js_path, 'a', encoding='utf-8') as f:
        f.write(search_js)
    print("Added search logic to main.js")
else:
    print("Search logic already exists in main.js")

