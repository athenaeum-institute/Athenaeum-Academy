import os
import glob

def rebrand_ai():
    target_dir = '/Users/ali/Documents/Academy'
    files_to_check = []
    
    # Collect all html and js files
    for root, _, files in os.walk(target_dir):
        if '.git' in root or 'node_modules' in root:
            continue
        for file in files:
            if file.endswith('.html') or file.endswith('.js') or file.endswith('.css') or file.endswith('.py'):
                files_to_check.append(os.path.join(root, file))
                
    for filepath in files_to_check:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content.replace('Athenaeum Assistant', 'Athenaeum Assistant')
        new_content = new_content.replace('athenaeum-assistant', 'athenaeum-assistant')
        new_content = new_content.replace('assistant-fab', 'assistant-fab')
        new_content = new_content.replace('assistant-chat-panel', 'assistant-chat-panel')
        
        # specifically update the prompt in athenaeum-assistant.js
        if filepath.endswith('athenaeum-assistant.js'):
            prompt_old = """You are Athenaeum Assistant, a personal AI teacher for students at Athenaeum Online Academy.

PERSONA:
- Your name is "Athenaeum Assistant" — a warm, encouraging personal tutor."""
            prompt_new = """You are Athenaeum Assistant, a personal AI teacher and website guide for students at Athenaeum Online Academy.

PERSONA:
- Your name is "Athenaeum Assistant" — a warm, encouraging personal tutor and platform guide.
- The student's name is "${name}". Use it occasionally to make responses personal.

WEBSITE GUIDE (IMPORTANT):
- You must guide students on how to use the Athenaeum website.
- If they want to buy a course, tell them to click the "Enroll Now" button on the course cards which takes them to checkout.
- If they want a trial, tell them to click "Free Trial" to view live class timings.
- After they purchase a course, tell them it will appear in their Student Dashboard, where they can access Live Classes, Recordings, and Mock Exams.
- If they ask about quizzes or mock exams, tell them to go to their course dashboard after enrolling."""
            
            new_content = new_content.replace(prompt_old, prompt_new)
            
        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {filepath}")

if __name__ == '__main__':
    rebrand_ai()
