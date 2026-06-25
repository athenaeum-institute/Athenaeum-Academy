import glob

html_files = glob.glob("*.html")
count = 0
for filepath in html_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace both variations of backticks inside alert() with single quotes
    new_content = content.replace(r'alert(`Coming Soon!`)', "alert('Coming Soon!')")
    new_content = new_content.replace(r'alert(\`Coming Soon!\`)', "alert('Coming Soon!')")

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        count += 1

print(f"Fixed alert backticks in {count} HTML files.")
