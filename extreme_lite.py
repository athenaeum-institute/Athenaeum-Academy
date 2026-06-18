import os
import re

css_file = '/Users/ali/Documents/Academy/styles.css'

with open(css_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Flatten Box Shadows for Performance
# Original:
#   --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
#   --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.06);
#   --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.08);
#   --shadow-xl: 0 20px 40px rgba(0, 80, 136, 0.08);
#   --shadow-teal: 0 8px 24px rgba(0, 210, 255, .20);

content = content.replace('--shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);', '--shadow-sm: 0 1px 2px rgba(0,0,0,0.02);')
content = content.replace('--shadow-md: 0 8px 24px rgba(0, 0, 0, 0.06);', '--shadow-md: 0 2px 4px rgba(0,0,0,0.03);')
content = content.replace('--shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.08);', '--shadow-lg: 0 4px 8px rgba(0,0,0,0.04);')
content = content.replace('--shadow-xl: 0 20px 40px rgba(0, 80, 136, 0.08);', '--shadow-xl: 0 4px 12px rgba(0,80,136,0.05);')
content = content.replace('--shadow-teal: 0 8px 24px rgba(0, 210, 255, .20);', '--shadow-teal: 0 4px 8px rgba(0,210,255,0.1);')

# 2. Prevent Layout Thrashing from 'transition: all'
# Replace `transition: all X` with `transition: opacity X, transform X, background-color X, border-color X, color X`
# But only for lines containing exactly "transition: all " to be safe.
def replace_transition(match):
    prefix = match.group(1)
    duration_easing = match.group(2)
    return f"{prefix}transition: opacity {duration_easing}, transform {duration_easing}, background-color {duration_easing}, border-color {duration_easing}, color {duration_easing};"

content = re.sub(r'([ \t]+)transition:\s*all\s+([^;]+);', replace_transition, content)

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied Extreme Lite Mode to styles.css")
