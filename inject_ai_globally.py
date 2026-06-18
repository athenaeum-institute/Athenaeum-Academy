import os
import glob
import re

html_files = glob.glob('/Users/ali/Documents/Academy/*.html')

css_tag = '<link rel="stylesheet" href="athenaeum-assistant.css?v=2">'
js_tag = '<script src="athenaeum-assistant.js?v=2" defer></script>'

for file in html_files:
    with open(file, 'r') as f:
        content = f.read()

    modified = False

    # Check and insert CSS in head
    if 'athenaeum-assistant.css' not in content:
        # Insert before </head>
        content = re.sub(r'(</head>)', f'  {css_tag}\n\\1', content, flags=re.IGNORECASE)
        modified = True

    # Check and insert JS before body closes
    if 'athenaeum-assistant.js' not in content:
        # Insert before </body>
        content = re.sub(r'(</body>)', f'  {js_tag}\n\\1', content, flags=re.IGNORECASE)
        modified = True

    if modified:
        with open(file, 'w') as f:
            f.write(content)
        print(f"Updated: {os.path.basename(file)}")

print("Done injecting globally.")
