import re

with open('course-details.html', 'r') as f:
    content = f.read()

# Replace the Sidebar CTA area to have a container we can inject into
content = re.sub(
    r'<a href="checkout\.html" class="btn btn-primary">Enroll Now</a>.*?<p style="text-align: center; font-size: 0\.85rem; color: var\(--clr-text-muted\);">Includes full lifetime access &.*?updates</p>',
    r'<div id="cd-action-btns"></div>\n        <p style="text-align: center; font-size: 0.85rem; color: var(--clr-text-muted);">Includes full lifetime access & updates</p>',
    content,
    flags=re.DOTALL
)

js_logic = """
  <script>
    document.addEventListener("DOMContentLoaded", async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const courseId = urlParams.get('id');

      if (!courseId || !window.AthenaeumCourses) {
        document.getElementById('error-content').style.display = 'block';
        return;
      }

      try {
        const course = await window.AthenaeumCourses.fetchCourseById(courseId);

        if (!course) {
          document.getElementById('error-content').style.display = 'block';
          return;
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

        const priceDisplay = formatPrice(course.price);
        const instructorName = course.profiles?.full_name || 'Instructor';
        const instructorAvatar = course.profiles?.avatar_url || 'https://via.placeholder.com/40';

        // Populate DOM
        document.getElementById('course-content').style.display = 'block';
        document.getElementById('bc-title').textContent = course.title;
        
        const badgeEl = document.getElementById('cd-category');
        badgeEl.innerHTML = `<span class="material-symbols-outlined">category</span> ${getCategoryLabel(course.category)}`;
        badgeEl.style = getCategoryBadgeStyle(course.category);
        
        document.getElementById('cd-title').textContent = course.title;
        
        // We do not have ratings in the new schema, hardcoding 4.9 for UI sake
        document.getElementById('cd-rating').textContent = '4.9';
        
        // We do not have enrolled count per course easily without grouping, keeping static for now
        document.getElementById('cd-enrolled').textContent = `New`;
        
        // Duration/Level fallback
        document.getElementById('cd-duration').textContent = `Self-paced`;
        document.getElementById('cd-level').textContent = course.subject || 'General';
        
        document.getElementById('cd-desc').textContent = course.description || 'No description provided.';
        document.getElementById('cd-image').src = course.thumbnail_url || 'https://via.placeholder.com/600x400';
        document.getElementById('cd-price').textContent = priceDisplay;
        document.getElementById('cd-instructor-img').src = instructorAvatar;
        document.getElementById('cd-instructor-name').textContent = instructorName;

        // Button logic
        const actionsContainer = document.getElementById('cd-action-btns');
        let targetUrl = 'auth.html?mode=register';
        if (window.currentUser) {
            targetUrl = `video-player.html?course=${course.id}`;
        }
        
        if (course.is_free_preview) {
           actionsContainer.innerHTML = `
             <a href="${targetUrl}" class="btn btn-outline" style="width: 100%; justify-content: center; padding: 1rem; font-size: 1.1rem; margin-bottom: 1rem; border: 2px solid var(--clr-primary); color: var(--clr-primary); text-decoration: none;">Start Free Preview</a>
             <a href="${targetUrl}" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 1rem; font-size: 1.1rem; margin-bottom: 1rem;">Enroll Full Course</a>
           `;
        } else {
           actionsContainer.innerHTML = `
             <a href="${targetUrl}" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 1rem; font-size: 1.1rem; margin-bottom: 1rem;">Enroll Now</a>
           `;
        }

        // Populate dynamic features
        let featuresHtml = '';
        if (course.what_you_will_learn && course.what_you_will_learn.length > 0) {
            course.what_you_will_learn.forEach(feature => {
                featuresHtml += `<li><span class="material-symbols-outlined">check_circle</span><span>${feature}</span></li>`;
            });
        } else {
            featuresHtml = `
              <li><span class="material-symbols-outlined">check_circle</span><span>Comprehensive syllabus coverage</span></li>
              <li><span class="material-symbols-outlined">check_circle</span><span>Step-by-step problem solving</span></li>
              <li><span class="material-symbols-outlined">check_circle</span><span>Past paper walkthroughs</span></li>
              <li><span class="material-symbols-outlined">check_circle</span><span>24/7 AI Tutor assistance</span></li>
            `;
        }
        document.getElementById('cd-features').innerHTML = featuresHtml;
      } catch (err) {
        console.error('Failed to load course details:', err);
        document.getElementById('error-content').style.display = 'block';
      }
    });
  </script>
"""

content = re.sub(
    r'<script>\s*document\.addEventListener\("DOMContentLoaded", async \(\) => \{.*?</script>',
    js_logic,
    content,
    flags=re.DOTALL
)

with open('course-details.html', 'w') as f:
    f.write(content)
