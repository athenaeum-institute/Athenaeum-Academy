import os
import glob
import re

workspace = '/Users/ali/Documents/Academy'

# Find all HTML files
html_files = glob.glob(os.path.join(workspace, '**', '*.html'), recursive=True)

# Add _headers and vercel.json
config_files = [
    os.path.join(workspace, '_headers'),
    os.path.join(workspace, 'vercel.json')
]

all_files = html_files + config_files

for filepath in all_files:
    if not os.path.exists(filepath):
        continue
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # We need to replace exactly what we injected.
        # It looks like: img-src 'self' data:; or similar.
        new_content = content.replace("img-src 'self' data:;", "img-src 'self' data: https:;")
        new_content = new_content.replace("img-src 'self' data:", "img-src 'self' data: https:")
        
        # Wait, if we replace "img-src 'self' data:", we might end up with "img-src 'self' data: https: https:" if run twice.
        # Let's use a regex that only replaces if https is not there
        new_content = re.sub(r"img-src\s+'self'\s+data:([^h]*)", r"img-src 'self' data: https:\1", content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

print("Done fixing CSP img-src!")
