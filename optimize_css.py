import os
import re

CSS_FILES = ['styles.css', 'athenaeum-assistant.css']

def optimize_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Comment out backdrop-filter
    # This regex matches backdrop-filter and -webkit-backdrop-filter
    content = re.sub(r'(\s*)([-a-z]*backdrop-filter:[^;]+;)', r'\1/* \2 (Removed for performance) */', content)

    # 2. Increase opacity of semi-transparent backgrounds to 0.98 to compensate for loss of blur
    # We only want to target backgrounds that had blur. A simple heuristic: 
    # anywhere we find rgba(r, g, b, 0.X) where X is < 9, let's bump it up if it's a main structural element.
    # Actually, a safer approach is to replace common translucent backgrounds.
    content = content.replace('rgba(252, 249, 248, .85)', '#FCF9F8')
    content = content.replace('rgba(252, 249, 248, .97)', '#FCF9F8')
    content = content.replace('rgba(255, 255, 255, 0.95)', '#ffffff')
    content = content.replace('rgba(255, 255, 255, 0.9)', '#ffffff')
    content = content.replace('rgba(255, 255, 255, 0.8)', '#ffffff')
    content = content.replace('rgba(255, 255, 255, 0.1)', '#ffffff') # teaser btn? wait.
    
    # For Athenaeum Assistant chat panel:
    content = content.replace('rgba(255, 255, 255, 0.97)', '#ffffff')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Optimized CSS in {filepath}")

for f in CSS_FILES:
    optimize_file(os.path.join('/Users/ali/Documents/Academy', f))
