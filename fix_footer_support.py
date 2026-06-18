import os
import re

directory = '/Users/ali/Documents/Academy'

new_support_links = """        <ul>
          <li><a href="privacy.html">Privacy Policy</a></li>
          <li><a href="terms.html">Terms of Service</a></li>
          <li><a href="refund.html">Refund Policy</a></li>
          <li><a href="cookie.html">Cookie Policy</a></li>
          <li><a href="security.html">Security</a></li>
        </ul>"""

for fname in os.listdir(directory):
    if fname.endswith('.html'):
        fpath = os.path.join(directory, fname)
        with open(fpath, 'r') as f:
            content = f.read()
        
        # Regex to find the support list
        pattern = r'<h4>Support</h4>\s*<ul>.*?</ul>'
        replacement = f'<h4>Support</h4>\n{new_support_links}'
        
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            if new_content != content:
                with open(fpath, 'w') as f:
                    f.write(new_content)
                print(f"Updated footer in {fname}")
