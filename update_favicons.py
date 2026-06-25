import os
import glob
import re

new_favicon = """<link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/favicon-180x180.png">
  <link rel="icon" type="image/png" sizes="192x192" href="/favicon-192x192.png">
  <link rel="icon" type="image/png" sizes="512x512" href="/favicon-512x512.png">"""

# Replace in all html files
html_files = glob.glob('**/*.html', recursive=True)
count = 0
for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find existing favicon tags
    # old pattern: <link rel="icon" type="image/png" href="logo_transparent.png" />
    # also handle ../logo_transparent.png
    pattern = re.compile(r'<link[^>]*rel=["\']icon["\'][^>]*>|<link[^>]*rel=["\']shortcut icon["\'][^>]*>')
    
    # Check if we have multiple tags, we should only replace the first one and delete others to avoid duplication
    # Or better: sub all of them, but we only want to insert the new_favicon ONCE.
    matches = pattern.findall(content)
    if matches:
        # replace the first match with the new favicon block
        first_match = matches[0]
        content = content.replace(first_match, new_favicon, 1)
        
        # remove the remaining matches
        for m in matches[1:]:
            content = content.replace(m + '\n', '')
            content = content.replace(m, '')
            
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
        print(f"Updated {file}")

print(f"Total files updated: {count}")
