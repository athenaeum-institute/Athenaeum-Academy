import glob
import re
import os

def fix_footer_links(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    prefix = "../" if "/" in filepath or "\\" in filepath else ""

    # 1. Social Links
    # Replace facebook
    content = re.sub(
        r'href="javascript:void\(0\)"\s+onclick="alert\(\'Coming Soon!\'\)"(\s+class="social-btn"\s+aria-label="Facebook"\s+id="social-facebook")',
        r'href="https://www.facebook.com/athenaeumacademy"\1',
        content
    )
    # Replace instagram
    content = re.sub(
        r'href="javascript:void\(0\)"\s+onclick="alert\(\'Coming Soon!\'\)"(\s+class="social-btn"\s+aria-label="Instagram"\s+id="social-instagram")',
        r'href="https://www.instagram.com/athenaeumacademy"\1',
        content
    )
    # Replace youtube
    content = re.sub(
        r'href="javascript:void\(0\)"\s+onclick="alert\(\'Coming Soon!\'\)"(\s+class="social-btn"\s+aria-label="YouTube"\s+id="social-youtube")',
        r'href="https://www.youtube.com/@athenaeumacademy"\1',
        content
    )

    # 2. Bottom Links
    content = re.sub(
        r'href="javascript:void\(0\)"\s+onclick="alert\(\'Coming Soon!\'\)">Privacy</a>',
        f'href="{prefix}privacy.html">Privacy</a>',
        content
    )
    content = re.sub(
        r'href="javascript:void\(0\)"\s+onclick="alert\(\'Coming Soon!\'\)">Terms</a>',
        f'href="{prefix}terms.html">Terms</a>',
        content
    )
    content = re.sub(
        r'href="javascript:void\(0\)"\s+onclick="alert\(\'Coming Soon!\'\)">Sitemap</a>',
        f'href="{prefix}sitemap.xml">Sitemap</a>',
        content
    )

    # 3. Athenaeum Assistant
    content = re.sub(
        r'href="javascript:void\(0\)"(\s+onclick="document.getElementById\(\'assistant-fab\'\))',
        r'href="#"\1',
        content
    )

    # 4. Copyright Year
    content = content.replace("© 2024", "© 2025")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fixed footer links in {filepath}")

if __name__ == "__main__":
    html_files = glob.glob("*.html") + glob.glob("about/*.html")
    for filepath in html_files:
        fix_footer_links(filepath)
    print("Done fixing footer links.")
