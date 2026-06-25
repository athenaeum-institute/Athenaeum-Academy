import glob
import re
import os
import json

def process_html_file(filepath, domain):
    if os.path.basename(filepath) == "index.html":
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    page_name = "Page"
    if title_match:
        # Get just the first part before the pipe if there is one
        full_title = title_match.group(1).strip()
        page_name = full_title.split('|')[0].strip()

    # Create schema
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": f"https://{domain}/"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": page_name,
                "item": f"https://{domain}/{filepath}"
            }
        ]
    }
    
    schema_str = f'\n  <script type="application/ld+json">\n{json.dumps(schema, separators=(",", ":"))}\n  </script>'

    # If already has BreadcrumbList, skip
    if '"@type":"BreadcrumbList"' in content:
        return

    # Insert into <head>
    new_content = re.sub(r'(</head>)', f'{schema_str}\n\\1', content, flags=re.IGNORECASE)

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Added Breadcrumb schema to {filepath}")

if __name__ == "__main__":
    domain = "athenaeumacademy.com"
    html_files = glob.glob("*.html") + glob.glob("about/*.html")
    for filepath in html_files:
        process_html_file(filepath, domain)
    print("Done adding Breadcrumb schemas.")
