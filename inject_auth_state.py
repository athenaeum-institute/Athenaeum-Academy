import glob
import os

files = glob.glob('*.html')
for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    # Don't inject if already there
    if 'auth-state.js' in content:
        continue

    # Find the line with supabase-client.js
    if 'supabase-client.js' in content:
        content = content.replace('<script src="supabase-client.js"></script>', '<script src="supabase-client.js"></script>\n  <script src="auth-state.js"></script>')
        with open(f, 'w') as file:
            file.write(content)
        print(f"Updated {f}")
