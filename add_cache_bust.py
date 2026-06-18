import os
import glob

html_files = glob.glob('/Users/ali/Documents/Academy/*.html')
for file in html_files:
    with open(file, 'r') as f:
        content = f.read()
    
    # Replace old references with ?v=2
    content = content.replace('athenaeum-assistant.css"', 'athenaeum-assistant.css?v=2"')
    content = content.replace('athenaeum-assistant.js"', 'athenaeum-assistant.js?v=2"')
    
    with open(file, 'w') as f:
        f.write(content)
print("Added cache busting query params to HTML files.")
