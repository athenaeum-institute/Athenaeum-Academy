import re
import os

files = ['/Users/ali/Documents/Academy/oa-levels.html', '/Users/ali/Documents/Academy/matric-inter.html']

for filepath in files:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r') as f:
        content = f.read()

    # The pattern matches the hardcoded button block
    pattern = re.compile(
        r'<div style="display:\s*flex;\s*gap:\s*0\.5rem;\s*padding:\s*0\s*1\.2rem\s*1\.2rem\s*1\.2rem;">\s*'
        r'<a href="trial-schedule\.html\?course=([cm][1-4])" class="btn"[^>]*>Free Trial</a>\s*'
        r'<a href="auth\.html\?mode=register&redirect=checkout\.html\?course=\1" class="btn btn-primary"[^>]*>Enroll Now</a>\s*'
        r'</div>'
    )

    def replacement(m):
        course_id = m.group(1)
        return (f'<div class="course-card-buttons" style="padding: 0 1.2rem 1.2rem 1.2rem;">\n'
                f'              <div class="row-1">\n'
                f'                <a href="trial-schedule.html?course={course_id}" class="btn" style="flex:1; justify-content:center; background:#eff6ff; color:var(--clr-primary); font-size:0.9rem; padding:0.6rem;">Free Trial</a>\n'
                f'                <a href="auth.html?mode=register&redirect=checkout.html?course={course_id}" class="btn btn-primary" style="flex:1; justify-content:center; font-size:0.9rem; padding:0.6rem;">Enroll Now</a>\n'
                f'              </div>\n'
                f'              <button class="add-to-cart-btn" onclick="addToCart(event, \'{course_id}\')" title="Add to Cart">\n'
                f'                <span class="material-symbols-outlined">shopping_cart</span> Add to Cart\n'
                f'              </button>\n'
                f'            </div>')

    new_content = pattern.sub(replacement, content)
    
    with open(filepath, 'w') as f:
        f.write(new_content)

print("Done")
