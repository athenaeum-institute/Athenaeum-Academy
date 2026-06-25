import glob
import re
import os

def update_footer(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Define the standardized Support block
    # We will adjust relative paths if the file is in a subdirectory (like about/)
    prefix = "../" if "/" in filepath or "\\" in filepath else ""
    
    standard_support = f"""<h4>Support</h4>
        <ul>
          <li><a href="{prefix}privacy.html">Privacy Policy</a></li>
          <li><a href="{prefix}terms.html">Terms of Service</a></li>
          <li><a href="{prefix}refund.html">Refund Policy</a></li>
          <li><a href="{prefix}cookie.html">Cookie Policy</a></li>
          <li><a href="{prefix}security.html">Security</a></li>
          <li><a href="{prefix}press.html">Press & Media</a></li>
        </ul>
        <div class="footer-contact-mini">
          <p><a href="mailto:support@athenaeumacademy.com" style="display:flex; align-items:center; gap:0.5rem;"><span class="material-symbols-outlined">mail</span> support@athenaeumacademy.com</a></p>
          <p><a href="tel:+923286715408" style="display:flex; align-items:center; gap:0.5rem;"><span class="material-symbols-outlined">call</span> +92 328 6715408</a></p>
          <p><span class="material-symbols-outlined">location_on</span> Lahore, Pakistan</p>
        </div>
      </div>"""

    # Regex to find the Support section and replace it
    # We look for <h4>Support</h4> up to the closing </div> of footer-col
    # followed by the closing </div> of footer-grid.
    pattern = re.compile(r'<h4>Support</h4>.*?</div>(\s*</div>\s*<div class="footer-bottom">)', re.DOTALL)
    
    if not pattern.search(content):
        print(f"Skipping {filepath}: Support section not found or format mismatch.")
        return

    new_content = pattern.sub(standard_support + r'\1', content)

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated footer NAP and Support links in {filepath}")

if __name__ == "__main__":
    html_files = glob.glob("*.html") + glob.glob("about/*.html")
    for filepath in html_files:
        update_footer(filepath)
    print("Done standardizing footers.")
