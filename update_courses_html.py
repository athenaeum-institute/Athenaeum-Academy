import re

with open('courses.html', 'r') as f:
    content = f.read()

tabs_html = """    <!-- Course filter tabs -->
    <div class="course-tabs" id="catalog-tabs" style="margin-bottom: 2rem; display: flex; flex-wrap: wrap; justify-content: center; gap: 8px;">
      <button class="tab-btn active" onclick="filterCatalog('all')" id="tab-all">All (<span id="count-all">0</span>)</button>
      <button class="tab-btn" onclick="filterCatalog('o_levels')" id="tab-o_levels">O Levels (<span id="count-o_levels">0</span>)</button>
      <button class="tab-btn" onclick="filterCatalog('a_levels')" id="tab-a_levels">A Levels (<span id="count-a_levels">0</span>)</button>
      <button class="tab-btn" onclick="filterCatalog('matric')" id="tab-matric">Matric (<span id="count-matric">0</span>)</button>
      <button class="tab-btn" onclick="filterCatalog('inter')" id="tab-inter">Inter (<span id="count-inter">0</span>)</button>
      <button class="tab-btn" onclick="filterCatalog('skill')" id="tab-skill">Skills (<span id="count-skill">0</span>)</button>
    </div>"""

content = re.sub(
    r'<!-- Course filter tabs -->.*?</div>',
    tabs_html,
    content,
    flags=re.DOTALL
)

js_logic = """
  <script>
    let allCourses = [];
    let userEnrollments = {};

    const formatPrice = (price) => {
      if (parseFloat(price) === 0) return 'FREE';
      return new Intl.NumberFormat('en-PK', { style: 'currency', currency: 'PKR', minimumFractionDigits: 0 }).format(price);
    };

    const getCategoryBadgeStyle = (category) => {
      switch (category) {
        case 'o_levels': return 'background: #005088; color: white; border: none;';
        case 'a_levels': return 'background: #7B2FBE; color: white; border: none;';
        case 'matric':   return 'background: #00A86B; color: white; border: none;';
        case 'inter':    return 'background: #FF6B35; color: white; border: none;';
        case 'skill':    return 'background: #FFD700; color: black; border: none;';
        default:         return 'background: #eee; color: #333; border: none;';
      }
    };

    const getCategoryLabel = (category) => {
      switch (category) {
        case 'o_levels': return 'O Levels';
        case 'a_levels': return 'A Levels';
        case 'matric': return 'Matric';
        case 'inter': return 'Inter';
        case 'skill': return 'Skills';
        default: return (category || '').toUpperCase();
      }
    };

    window.filterCatalog = (category) => {
      // Update active tab
      document.querySelectorAll('#catalog-tabs .tab-btn').forEach(btn => btn.classList.remove('active'));
      document.getElementById('tab-' + category).classList.add('active');

      const grid = document.getElementById('courses-grid');
      grid.style.opacity = '0';
      
      setTimeout(() => {
        renderCourses(category);
        grid.style.opacity = '1';
      }, 300);
    };

    const updateCounts = () => {
      const counts = { all: allCourses.length, o_levels: 0, a_levels: 0, matric: 0, inter: 0, skill: 0 };
      allCourses.forEach(c => {
        if (counts[c.category] !== undefined) counts[c.category]++;
      });
      for (const [cat, count] of Object.entries(counts)) {
        const el = document.getElementById('count-' + cat);
        if (el) el.innerText = count;
      }
    };

    const renderCourses = (filterCat) => {
      const grid = document.getElementById('courses-grid');
      let filtered = allCourses;
      
      if (filterCat !== 'all') {
        filtered = allCourses.filter(c => c.category === filterCat);
      }

      if (filtered.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">No courses found in this category.</p>';
        return;
      }

      let html = '';
      filtered.forEach(course => {
        const priceDisplay = formatPrice(course.price);
        const badgeStyle = getCategoryBadgeStyle(course.category);
        const badgeLabel = getCategoryLabel(course.category);
        
        let buttonsHtml = '';
        const enrollRecord = userEnrollments[course.id];
        const isPaid = enrollRecord && (enrollRecord.payment_status === 'paid' || enrollRecord.status === 'active' || enrollRecord.status === 'paid');
        const isTrial = enrollRecord && (enrollRecord.payment_status === 'free' || enrollRecord.status === 'free_trial');

        if (isPaid) {
          buttonsHtml = `<a href="video-player.html?course=${course.id}" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Continue Learning &rarr;</a>`;
        } else if (isTrial) {
          buttonsHtml = `
            <a href="video-player.html?course=${course.id}" class="btn" style="flex:1; justify-content:center; background:#eff6ff; color:var(--clr-primary); font-size:0.9rem; padding:0.6rem;">Continue Trial &rarr;</a>
            <a href="checkout.html?course=${course.id}" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Upgrade to Full Access</a>
          `;
        } else {
          let checkoutUrl = window.currentUser ? `checkout.html?course=${course.id}` : `auth.html?mode=register&redirect=checkout.html?course=${course.id}`;
          let trialUrl = `trial-schedule.html?course=${course.id}`;
          buttonsHtml = `
            <a href="${trialUrl}" class="btn" style="flex:1; justify-content:center; background:#eff6ff; color:var(--clr-primary); font-size:0.9rem; padding:0.6rem;">Free Trial</a>
            <a href="${checkoutUrl}" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Enroll Now</a>
          `;
        }

        html += `
          <article class="course-card" style="display: flex; flex-direction: column;">
            <a href="course-details.html?id=${course.id}" style="text-decoration: none; color: inherit; display: block; flex: 1;">
              <div class="course-thumb">
                <img src="${course.thumbnail_url || 'https://via.placeholder.com/400x250'}" alt="${course.title}" loading="lazy" />
                <span class="board-badge" style="${badgeStyle}">${badgeLabel}</span>
              </div>
              <div class="course-body" style="flex: 1; display: flex; flex-direction: column;">
                <h3 class="course-title" style="margin-top:0.5rem; margin-bottom: 0.5rem; font-size: 1.2rem;">${course.title}</h3>
                <div class="course-meta" style="margin-bottom: auto;">
                  <span><span class="material-symbols-outlined" style="font-size:18px;">book</span> ${course.subject || 'General'}</span>
                </div>
                <div class="course-footer" style="margin-top: 1rem; border-top: 1px solid #eee; padding-top: 1rem; display: flex; justify-content: space-between; align-items: center;">
                  <span class="course-price" style="color: var(--clr-primary); font-weight: 800; font-size: 1.2rem;">${priceDisplay}</span>
                  ${course.is_free_preview ? '<span style="font-size:0.8rem; background:#f0f9ff; color:#0284c7; padding:4px 8px; border-radius:12px; font-weight:600;">Free Preview</span>' : ''}
                </div>
              </div>
            </a>
            <div style="display: flex; gap: 0.5rem; padding: 0 1.2rem 1.2rem 1.2rem;">
              ${buttonsHtml}
            </div>
          </article>
        `;
      });
      
      grid.innerHTML = html;
    };

    document.addEventListener('DOMContentLoaded', async () => {
      const grid = document.getElementById('courses-grid');
      if(!grid || !window.AthenaeumCourses) return;
      
      // Ensure smooth transition for filtering
      grid.style.transition = 'opacity 0.3s ease';
      
      const skeletonHTML = `
        <div class="course-skeleton">
          <div class="skeleton-thumb"></div>
          <div class="skeleton-body">
            <div class="skeleton-line" style="width: 40%"></div>
            <div class="skeleton-line" style="height: 24px; margin: 12px 0;"></div>
            <div class="skeleton-line" style="width: 60%"></div>
            <div class="skeleton-footer">
              <div class="skeleton-avatar"></div>
              <div class="skeleton-line" style="width: 30%; margin:0;"></div>
            </div>
          </div>
        </div>
      `.repeat(6);
      grid.innerHTML = skeletonHTML;
      
      try {
        window.currentUser = await getCurrentUser();
        if (window.currentUser) {
          userEnrollments = await window.AthenaeumCourses.getUserEnrollmentMap(window.currentUser.id);
        }
        allCourses = await window.AthenaeumCourses.fetchAllCourses();
        updateCounts();
        
        // Parse URL tab query param if exists
        const urlParams = new URLSearchParams(window.location.search);
        let startTab = urlParams.get('tab') || 'all';
        if (!['all', 'o_levels', 'a_levels', 'matric', 'inter', 'skill'].includes(startTab)) startTab = 'all';
        
        filterCatalog(startTab);
      } catch (err) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: red;">Failed to load courses. Please try again later.</p>';
        console.error('Render error:', err);
      }
    });
  </script>
"""

content = re.sub(
    r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', async \(\) => \{.*?</script>',
    js_logic,
    content,
    flags=re.DOTALL
)

with open('courses.html', 'w') as f:
    f.write(content)
