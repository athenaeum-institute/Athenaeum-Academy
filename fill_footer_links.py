import os

files_to_update = ['index.html', 'matric-inter.html', 'oa-levels.html']

target_block = """        <ul>
        </ul>"""

replacement_block = """        <ul>
          <li><a href="#how-it-works">How It Works</a></li>
          <li><a href="auth.html?mode=register">Free Trial</a></li>
          <li><a href="live-class.html">Live Classes</a></li>
          <li><a href="mock-exam.html">Mock Exams</a></li>
          <li><a href="javascript:void(0)" onclick="document.getElementById('ustad-fab') ? document.getElementById('ustad-fab').click() : alert('Ustad AI is not available')">Ustad AI Tutor</a></li>
        </ul>"""

for file_name in files_to_update:
    file_path = os.path.join('/Users/ali/Documents/Academy', file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # We need to find the specific <ul> under <h4>Academy</h4>
        # Because replacing all empty <ul> could affect other parts if any exist
        
        target_academy = "<h4>Academy</h4>\n        <ul>\n        </ul>"
        replacement_academy = f"<h4>Academy</h4>\n{replacement_block}"
        
        if target_academy in content:
            content = content.replace(target_academy, replacement_academy)
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Updated {file_name}")
        else:
            print(f"Target block not found in {file_name}")
    else:
        print(f"File {file_name} not found")
