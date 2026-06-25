import glob
import re

html_files = glob.glob("*.html")
count = 0
for filepath in html_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix the stray slash before loading="lazy"
    new_content = re.sub(r'\s*/\s*loading="lazy"([^>]*)>', r' loading="lazy"\1 />', content)

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        count += 1

print(f"Fixed malformed image tags in {count} files.")
