import re

def update_file(filename, is_index):
    with open(filename, 'r') as f:
        content = f.read()

    # Update grid classes
    if is_index:
        content = content.replace('class="courses-grid"', 'class="courses-scroll-container"')
    else:
        content = content.replace('class="courses-grid"', 'class="courses-catalog-grid"')

    # Update button HTML in the JS template
    btn_html_old = r'<div style="padding: 0 1\.5rem 1\.5rem;">\s*<a href="\$\{targetUrl\}" class="btn btn-primary" style="width: 100%; text-align: center; display: block;">\$\{btnText\}</a>\s*</div>'
    
    # We will replace it with the new class `course-card-btn`
    btn_html_new = r'<a href="${targetUrl}" class="course-card-btn ${course.is_free_preview && window.currentUser ? \'outline\' : \'\'}">${btnText}</a>'
    
    content = re.sub(btn_html_old, btn_html_new, content)
    
    # Let's also remove inline styles from the card wrapper and body to rely on CSS
    content = content.replace('style="display: flex; flex-direction: column;"', '')
    content = content.replace('style="flex: 1; display: flex; flex-direction: column;"', '')
    content = content.replace('style="margin-top:0.5rem; margin-bottom: 0.5rem; font-size: 1.2rem;"', '')
    content = content.replace('style="margin-bottom: auto;"', '')
    content = content.replace('style="margin-top: 1rem; border-top: 1px solid #eee; padding-top: 1rem; display: flex; justify-content: space-between; align-items: center;"', '')
    content = content.replace('style="color: var(--clr-primary); font-weight: 800; font-size: 1.2rem;"', '')
    
    with open(filename, 'w') as f:
        f.write(content)

update_file('courses.html', False)
update_file('index.html', True)
