import os
import glob

# The string to search for and the string to insert before it
search_str = '<li><a href="about.html" class="nav-link">About</a></li>'
insert_str = '<li><a href="community.html" class="nav-link">Community Feed</a></li>\n        '

# Find all HTML files
html_files = glob.glob('*.html')

for file_path in html_files:
    # Skip dashboard files as they don't have this public nav structure
    if file_path.startswith('dashboard') or file_path in ['admin.html', 'community.html', 'auth.html', 'video-player.html']:
        continue

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if search_str in content and insert_str.strip() not in content:
        # Replace first occurrence or all occurrences
        content = content.replace(search_str, f'{insert_str}{search_str}')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated navbar in {file_path}")
    else:
        print(f"Skipped {file_path} (already updated or nav not found)")

print("Done updating navbars.")
