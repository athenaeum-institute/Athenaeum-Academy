import os
import glob
import re

workspace = '/Users/ali/Documents/Academy'

html_files = glob.glob(os.path.join(workspace, '**', '*.html'), recursive=True)

for filepath in html_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the img-src line entirely to ensure https: is included
        # Previous format: img-src 'self' data: blob: https://*.supabase.co...
        # Or img-src 'self' data: https: blob: ...
        # We will replace any img-src definition with our relaxed one:
        
        new_content = re.sub(
            r"img-src\s+'self'[^;]*;", 
            "img-src 'self' data: https: blob:;", 
            content
        )
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
    except Exception as e:
        pass

print("Done")
