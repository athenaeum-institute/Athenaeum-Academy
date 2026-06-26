import os
import re
import json

NEW_TAGS = """  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/favicon-180x180.png">
  <link rel="icon" type="image/png" sizes="192x192" href="/favicon-192x192.png">
  <link rel="icon" type="image/png" sizes="512x512" href="/favicon-512x512.png">"""

edits = []

def process_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all lines with favicon tags
    lines = content.split('\n')
    start_line = -1
    end_line = -1
    
    pattern = re.compile(r'<link[^>]*?rel=["\'][^"\']*?(?:icon|apple-touch-icon)[^"\']*?["\'][^>]*>', re.IGNORECASE)
    
    for i, line in enumerate(lines):
        if pattern.search(line):
            if start_line == -1:
                start_line = i
            end_line = i
            
    if start_line == -1:
        return
        
    target = '\n'.join(lines[start_line:end_line+1])
    replacement = NEW_TAGS
    
    edits.append({
        "TargetFile": file_path,
        "StartLine": start_line + 1,
        "EndLine": end_line + 1,
        "TargetContent": target,
        "ReplacementContent": replacement
    })

if __name__ == '__main__':
    for root, dirs, files in os.walk('/Users/ali/Documents/Academy'):
        if 'api' in root:
            continue
        for file in files:
            if file.endswith('.html'):
                process_html_file(os.path.join(root, file))
    
    for edit in edits:
        print(f"--- FILE START: {edit['TargetFile']}")
        print(f"START_LINE: {edit['StartLine']}")
        print(f"END_LINE: {edit['EndLine']}")
        print(f"=== TARGET ===")
        print(edit['TargetContent'])
        print(f"=== REPLACEMENT ===")
        print(edit['ReplacementContent'])
        print(f"--- FILE END")
