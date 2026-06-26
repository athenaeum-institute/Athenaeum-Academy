import os
import re
import glob

workspace = '/Users/ali/Documents/Academy'

html_files = []
for root, _, files in os.walk(workspace):
    if '.gemini' in root or '.agents' in root:
        continue
    for file in files:
        if file.endswith('.html'):
            html_files.append(os.path.join(root, file))

security_headers = """
  <!-- Security Headers -->
  <meta http-equiv="X-Frame-Options" content="DENY">
  <meta http-equiv="X-XSS-Protection" content="1; mode=block">
  <meta http-equiv="X-Content-Type-Options" content="nosniff">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://meet.jit.si https://cdn.emailjs.com https://www.googletagmanager.com https://apis.google.com;
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com;
    font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com;
    img-src 'self' data: blob: https://*.supabase.co https://*.googleusercontent.com https://custom-images.strikinglycdn.com;
    connect-src 'self' https://*.supabase.co https://api.emailjs.com https://meet.jit.si;
    frame-src https://meet.jit.si https://hcaptcha.com https://*.hcaptcha.com;
  ">
"""

for filepath in html_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        continue

    # Add security headers to <head> if not already there
    if 'X-Frame-Options' not in content:
        # Find the end of <head>
        head_match = re.search(r'</head>', content, re.IGNORECASE)
        if head_match:
            idx = head_match.start()
            content = content[:idx] + security_headers + content[idx:]

    # Secure target="_blank" links
    # Find all <a ... target="_blank" ...> and ensure rel="noopener noreferrer"
    # We will use a regex substitution
    
    def secure_link(match):
        full_tag = match.group(0)
        # Check if it already has rel=
        if 'rel=' in full_tag:
            # If it has rel, ensure noopener noreferrer is in it
            # This is tricky without a proper HTML parser, but we can do a simpler replace
            # since most of our links either don't have rel, or have rel="noopener".
            if 'noopener noreferrer' not in full_tag:
                full_tag = re.sub(r'rel="([^"]*)"', r'rel="\1 noopener noreferrer"', full_tag)
                # Cleanup duplicates if any
                full_tag = full_tag.replace('noopener noopener', 'noopener').replace('noreferrer noreferrer', 'noreferrer')
        else:
            # Inject rel="noopener noreferrer"
            full_tag = full_tag.replace('target="_blank"', 'target="_blank" rel="noopener noreferrer"')
        return full_tag

    content = re.sub(r'<a\s+[^>]*target="_blank"[^>]*>', secure_link, content, flags=re.IGNORECASE)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        pass

print("Applied security headers and link sanitization.")
