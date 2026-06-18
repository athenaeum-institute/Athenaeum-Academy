import re

# 1. Update index.html
with open('/Users/ali/Documents/Academy/index.html', 'r') as f:
    html = f.read()

# Add inline padding to stories section
html = html.replace('<section class="stories section" id="success-stories">', 
                    '<section class="stories section" id="success-stories" style="padding: 4rem 0;">')

# Reduce margin of section title inside success-stories
# Since there are multiple <h2 class="section-title center">, we only want the one in Student Achievements.
html = html.replace('<h2 class="section-title center">Real Results. Real Students.</h2>',
                    '<h2 class="section-title center" style="margin-bottom: 0.5rem; font-size: 2.2rem;">Real Results. Real Students.</h2>')

html = html.replace('<p class="section-subtitle">Over 16,500 students have transformed their academic futures with Athenaeum</p>',
                    '<p class="section-subtitle" style="font-size: 0.95rem; margin-bottom: 1.5rem;">Over 16,500 students have transformed their academic futures with Athenaeum</p>')

with open('/Users/ali/Documents/Academy/index.html', 'w') as f:
    f.write(html)

# 2. Update styles.css
with open('/Users/ali/Documents/Academy/styles.css', 'r') as f:
    css = f.read()

replacements = {
    'padding: 80px 0;': 'padding: 40px 0;',
    'gap: 60px;': 'gap: 40px;',
    'margin: 60px auto 0;': 'margin: 30px auto 0;',
    'width: 380px;\n  height: 380px;': 'width: 300px;\n  height: 300px;',
    'top: 35px; left: 35px; right: 35px; bottom: 35px;': 'top: 25px; left: 25px; right: 25px; bottom: 25px;',
    'width: 140px; height: 140px;': 'width: 100px; height: 100px;',
    'width: 64px; height: 64px;\n  margin: -32px 0 0 -32px;\n  transform: rotate(var(--angle)) translateY(-190px);': 'width: 48px; height: 48px;\n  margin: -24px 0 0 -24px;\n  transform: rotate(var(--angle)) translateY(-150px);',
    'font-size: 18px;\n  border: 4px solid var(--clr-white);': 'font-size: 14px;\n  border: 3px solid var(--clr-white);',
    'padding: 50px 40px;\n  border-radius: var(--radius-xl);\n  box-shadow: 0 20px 48px rgba(0, 80, 136, 0.08);': 'padding: 30px 24px;\n  border-radius: 16px;\n  box-shadow: 0 10px 30px rgba(0, 80, 136, 0.05);',
    'top: -15px; left: -10px;\n  font-family: var(--font-heading);\n  font-size: 10rem;': 'top: -5px; left: -5px;\n  font-family: var(--font-heading);\n  font-size: 6rem;',
    'top: 30px; right: 30px;\n  padding: 6px 16px;\n  border-radius: var(--radius);\n  font-family: var(--font-heading);\n  font-size: 14px; font-weight: 800;': 'top: 20px; right: 20px;\n  padding: 4px 12px;\n  border-radius: 8px;\n  font-family: var(--font-heading);\n  font-size: 12px; font-weight: 800;',
    'font-size: 18px;\n  color: var(--clr-on-surface);\n  line-height: 1.8;\n  margin-bottom: 30px;': 'font-size: 14px;\n  color: var(--clr-on-surface);\n  line-height: 1.6;\n  margin-bottom: 20px;',
    'padding-top: 20px;\n  margin-bottom: 20px;': 'padding-top: 15px;\n  margin-bottom: 15px;',
    '.orbit-author h4 {\n  font-family: var(--font-heading);\n  font-size: 20px;': '.orbit-author h4 {\n  font-family: var(--font-heading);\n  font-size: 16px;',
    '.orbit-author p {\n  font-size: 14px;': '.orbit-author p {\n  font-size: 12px;',
    'padding: 6px 14px; border-radius: var(--radius); font-size: 12px;': 'padding: 4px 10px; border-radius: 6px; font-size: 11px;'
}

for old, new in replacements.items():
    if old in css:
        css = css.replace(old, new)
    else:
        print(f"Warning: Could not find '{old}'")

with open('/Users/ali/Documents/Academy/styles.css', 'w') as f:
    f.write(css)

print("Applied compact scaling to Orbit section")
