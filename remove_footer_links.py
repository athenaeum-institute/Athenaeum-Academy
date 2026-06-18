import os

files_to_update = ['index.html', 'matric-inter.html', 'oa-levels.html']

for file_name in files_to_update:
    file_path = os.path.join('/Users/ali/Documents/Academy', file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # The block to remove
        target_block = """        <ul>
          <li><a href="about.html">About Us</a></li>
          <li><a href="about.html">Our Teachers</a></li>
          <li><a href="about.html">Success Stories</a></li>
          <li><a href="dashboard-parent.html">Parent Reviews</a></li>
          <li><a href="about.html">Blog &amp; Articles</a></li>
          <li><a href="contact.html">Contact Us</a></li>
        </ul>"""
        
        if target_block in content:
            content = content.replace(target_block, "        <ul>\n        </ul>")
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Updated {file_name}")
        else:
            print(f"Target block not found in {file_name}")
    else:
        print(f"File {file_name} not found")
