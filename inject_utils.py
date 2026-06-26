import os
import re

workspace = '/Users/ali/Documents/Academy'
for root, _, files in os.walk(workspace):
    if '.gemini' in root or '.agents' in root:
        continue
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue
            
            if '<script src="utils.js"></script>' not in content and '<script src="../utils.js"></script>' not in content:
                # determine depth for relative path
                depth = filepath.replace(workspace, '').count('/') - 1
                prefix = '../' * depth if depth > 0 else ''
                script_tag = f'\n  <script src="{prefix}utils.js"></script>'
                
                # inject before </head>
                content = re.sub(r'(</head>)', f'{script_tag}\n\\1', content, flags=re.IGNORECASE)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

print("Injected utils.js")
