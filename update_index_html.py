import re

with open('index.html', 'r') as f:
    content = f.read()

# We need to remove the hardcoded course tabs and the static cards inside courses-grid
replacement_html = """        <!-- Cards grid -->
        <div class="courses-grid" id="home-featured-courses">
          <!-- Skeletons while loading -->
          <div class="course-skeleton"><div class="skeleton-thumb"></div><div class="skeleton-body"><div class="skeleton-line" style="width:40%"></div><div class="skeleton-line" style="height:24px;margin:12px 0;"></div><div class="skeleton-line" style="width:60%"></div></div></div>
          <div class="course-skeleton"><div class="skeleton-thumb"></div><div class="skeleton-body"><div class="skeleton-line" style="width:40%"></div><div class="skeleton-line" style="height:24px;margin:12px 0;"></div><div class="skeleton-line" style="width:60%"></div></div></div>
          <div class="course-skeleton"><div class="skeleton-thumb"></div><div class="skeleton-body"><div class="skeleton-line" style="width:40%"></div><div class="skeleton-line" style="height:24px;margin:12px 0;"></div><div class="skeleton-line" style="width:60%"></div></div></div>
          <div class="course-skeleton"><div class="skeleton-thumb"></div><div class="skeleton-body"><div class="skeleton-line" style="width:40%"></div><div class="skeleton-line" style="height:24px;margin:12px 0;"></div><div class="skeleton-line" style="width:60%"></div></div></div>
          <div class="course-skeleton"><div class="skeleton-thumb"></div><div class="skeleton-body"><div class="skeleton-line" style="width:40%"></div><div class="skeleton-line" style="height:24px;margin:12px 0;"></div><div class="skeleton-line" style="width:60%"></div></div></div>
          <div class="course-skeleton"><div class="skeleton-thumb"></div><div class="skeleton-body"><div class="skeleton-line" style="width:40%"></div><div class="skeleton-line" style="height:24px;margin:12px 0;"></div><div class="skeleton-line" style="width:60%"></div></div></div>
        </div><!-- /.courses-grid -->

        <div class="courses-cta">
          <a href="courses.html" class="btn btn-primary btn-lg" id="view-all-courses">
            View All Courses &rarr;
          </a>
        </div>

        <script>
          document.addEventListener('DOMContentLoaded', async () => {
            const grid = document.getElementById('home-featured-courses');
            if(!grid || !window.AthenaeumCourses) return;
            
            try {
              const allCourses = await window.AthenaeumCourses.fetchAllCourses();
              const userEnrollments = window.currentUser ? await window.AthenaeumCourses.getUserEnrollmentMap(window.currentUser.id) : {};
              
              const oLevels = allCourses.filter(c => c.category === 'o_levels').slice(0, 2);
              const matric = allCourses.filter(c => c.category === 'matric').slice(0, 2);
              const inter = allCourses.filter(c => c.category === 'inter').slice(0, 2);
              
              let featured = [...oLevels, ...matric, ...inter];
              
              if (featured.length === 0) {
                  featured = allCourses.slice(0, 6);
              }
              
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

              let html = '';
              featured.forEach(course => {
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
            } catch (err) {
              console.error('Featured courses render error:', err);
              grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: red;">Failed to load featured courses.</p>';
            }
          });
        </script>"""

# Replace from <!-- Course filter tabs --> down to </a> \n </div> inside .courses-cta section
content = re.sub(
    r'<!-- Course filter tabs -->.*?View All Courses &rarr;\s*</a>\s*</div>',
    replacement_html,
    content,
    flags=re.DOTALL
)

with open('index.html', 'w') as f:
    f.write(content)
