import os

directory = '/Users/ali/Documents/Academy'

def revert_cap_in_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # 1. Reverse the plain text replacements first to avoid partial matches
                    content = content.replace('<span class="logo-tagline">Learn with</span> Athenaeum', '🎓 Athenaeum')
                    
                    # 2. Reverse the logo-icon replacement
                    content = content.replace('<span class="logo-tagline">Learn with</span>', '<span class="logo-icon">🎓</span>')
                    
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Reverted: {file_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

revert_cap_in_files(directory)
