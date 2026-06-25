import os
import re

count = 0
for filename in os.listdir('.'):
    if filename.endswith('.html'):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Only modify if 'become-a-teacher.html' not already there
        if 'become-a-teacher.html' not in content:
            # We want to add it under Academy, right after Athenaeum Assistant Tutor
            pattern = r'(<a href="javascript:void\(0\)" onclick="document\.getElementById\(\'assistant-fab\'\).*?>Athenaeum Assistant Tutor</a></li>)'
            new_link = r'\1\n          <li><a href="become-a-teacher.html">Become a Teacher</a></li>'
            
            updated_content = re.sub(pattern, new_link, content)
            
            if content != updated_content:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"Updated {filename}")
                count += 1

print(f"Updated {count} files.")
