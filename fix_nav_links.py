import os, glob

files = glob.glob('**/*.html', recursive=True)
changed = []
for f in files:
    with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
        content = fh.read()
    new = content
    new = new.replace('href="oa-levels.html"', 'href="courses.html"')
    new = new.replace('href="matric-inter.html"', 'href="courses.html"')
    new = new.replace('href="../oa-levels.html"', 'href="../courses.html"')
    new = new.replace('href="../matric-inter.html"', 'href="../courses.html"')
    if new != content:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(new)
        changed.append(f)

print(f"Updated {len(changed)} files:")
for c in changed:
    print(f"  {c}")
