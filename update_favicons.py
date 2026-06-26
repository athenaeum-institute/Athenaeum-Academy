import os
import re

NEW_TAGS = """  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/favicon-180x180.png">
  <link rel="icon" type="image/png" sizes="192x192" href="/favicon-192x192.png">
  <link rel="icon" type="image/png" sizes="512x512" href="/favicon-512x512.png">"""

def process_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove existing favicon tags along with leading whitespace and trailing newline
    pattern_with_space = re.compile(r'^[ \t]*<link[^>]*?rel=["\'][^"\']*?(?:icon|apple-touch-icon)[^"\']*?["\'][^>]*>\n?', re.IGNORECASE | re.MULTILINE)
    new_content = pattern_with_space.sub('', content)
    
    # Catch any remaining inline ones
    pattern_inline = re.compile(r'<link[^>]*?rel=["\'][^"\']*?(?:icon|apple-touch-icon)[^"\']*?["\'][^>]*>', re.IGNORECASE)
    new_content = pattern_inline.sub('', new_content)
    
    # Insert new tags just before </head>
    if '</head>' in new_content:
        new_content = new_content.replace('</head>', f'{NEW_TAGS}\n</head>')
    elif '</HEAD>' in new_content:
        new_content = new_content.replace('</HEAD>', f'{NEW_TAGS}\n</HEAD>')

    if new_content != content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {file_path}")
        except Exception as e:
            print(f"Failed to update {file_path}: {e}")
            # Save the new content somewhere we CAN write, so we can use it with write_to_file
            failed_dir = os.path.join('/Users/ali/Documents/Academy', 'failed_updates')
            os.makedirs(failed_dir, exist_ok=True)
            with open(os.path.join(failed_dir, os.path.basename(file_path)), 'w', encoding='utf-8') as f:
                f.write(new_content)

if __name__ == '__main__':
    for root, dirs, files in os.walk('/Users/ali/Documents/Academy'):
        if 'failed_updates' in root:
            continue
        for file in files:
            if file.endswith('.html'):
                process_html_file(os.path.join(root, file))
