import re

# 1. Update index.html
with open('/Users/ali/Documents/Academy/index.html', 'r') as f:
    html = f.read()

# Add inline padding to parent-trust section to make it compact
html = html.replace('<section class="parent-trust section section--alt" id="parent-trust">', 
                    '<section class="parent-trust section section--alt" id="parent-trust" style="padding: 4rem 0;">')
# Reduce margin of section title
html = html.replace('<h2 class="section-title center">Trusted by Parents Across Pakistan</h2>',
                    '<h2 class="section-title center" style="margin-bottom: 0.5rem; font-size: 2.2rem;">Trusted by Parents Across Pakistan</h2>')
html = html.replace('<p class="section-subtitle">Parents choose Athenaeum because they see real, measurable results in their',
                    '<p class="section-subtitle" style="font-size: 0.95rem; margin-bottom: 1.5rem;">Parents choose Athenaeum because they see real, measurable results in their')

with open('/Users/ali/Documents/Academy/index.html', 'w') as f:
    f.write(html)

# 2. Update styles.css
with open('/Users/ali/Documents/Academy/styles.css', 'r') as f:
    css = f.read()

# Compact .parent-grid gap
css = css.replace('gap: var(--sp-10);', 'gap: var(--sp-6);')

# Compact trust badges
css = css.replace('padding: 6px 16px;\n  font-size: 12px;', 'padding: 4px 12px;\n  font-size: 11px;')

# Add energetic hover to trust badge
css = css.replace('box-shadow: 0 0 0 3px rgba(17, 202, 160, .1);', 'box-shadow: 0 4px 12px rgba(0, 210, 255, 0.2); background: rgba(0, 210, 255, 0.05);')

# Compact parent-testimonials gap
css = css.replace('gap: var(--sp-6);\n  align-items: start;', 'gap: 1rem;\n  align-items: start;')

# Compact parent-card padding and quote
css = css.replace('.parent-card {\n  background: var(--clr-white);\n  border-radius: var(--radius-xl);\n  padding: 20px;', 
                  '.parent-card {\n  background: var(--clr-white);\n  border-radius: 16px;\n  padding: 16px;')

css = css.replace('.parent-quote {\n  font-size: 14px;\n  line-height: 1.6;\n  margin-bottom: 16px;', 
                  '.parent-quote {\n  font-size: 13px;\n  line-height: 1.5;\n  margin-bottom: 12px;')

# Enhance featured card
css = css.replace('.parent-card--featured {\n  background: var(--clr-primary);\n  color: #fff;\n  border-color: var(--clr-primary);\n  box-shadow: var(--shadow-xl);\n  transform: translateY(-8px);\n}',
                  '.parent-card--featured {\n  background: linear-gradient(135deg, #0A0E27, #005088);\n  color: #fff;\n  border-color: transparent;\n  box-shadow: 0 10px 30px rgba(0, 80, 136, 0.4);\n  transform: translateY(-4px);\n}')

css = css.replace('box-shadow: 0 28px 56px rgba(0, 80, 136, .30);', 'box-shadow: 0 15px 40px rgba(0, 210, 255, 0.3);')

# Compact avatar
css = css.replace('.parent-avatar {\n  width: 40px;\n  height: 40px;', '.parent-avatar {\n  width: 32px;\n  height: 32px;')

with open('/Users/ali/Documents/Academy/styles.css', 'w') as f:
    f.write(css)

print("Applied compact energetic styling to Parent Trust section")
