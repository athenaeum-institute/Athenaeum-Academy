import os
import glob
import re

html_files = glob.glob("*.html")
for filepath in html_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all <img ...> tags
    def add_lazy(match):
        img_tag = match.group(0)
        # Skip if already has loading="lazy"
        if 'loading="lazy"' in img_tag or "loading='lazy'" in img_tag:
            return img_tag
        
        # Heuristic: skip images with 'hero', 'logo', or 'banner' in their classes/src, as they are usually above the fold
        if 'hero' in img_tag.lower() or 'logo' in img_tag.lower() or 'banner' in img_tag.lower():
            return img_tag
            
        # Add loading="lazy" before the closing bracket
        return img_tag[:-1] + ' loading="lazy">'

    new_content = re.sub(r'<img\s+[^>]+>', add_lazy, content)

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

print("Added loading='lazy' to images below the fold.")
