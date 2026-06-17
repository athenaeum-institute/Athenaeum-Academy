import re

with open('/Users/ali/Documents/Academy/styles.css', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the errant parent-card--feat.course-card:hover block
content = re.sub(
    r'\.parent-card--feat\.course-card:hover \{\s*transform: translateY\(-4px\);\s*box-shadow: 0 12px 32px rgba\(123, 44, 191, \.15\), 0 4px 12px rgba\(255, 0, 110, \.1\);\s*\}',
    '',
    content
)

# 2. Update .course-card:hover
course_card_old = """.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 80, 136, .08);
}"""

course_card_new = """.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(123, 44, 191, .15), 0 4px 12px rgba(255, 0, 110, .1);
}"""

content = content.replace(course_card_old, course_card_new)

# 3. Update .chip (let's do .chip--teal and .chip--gold as well)
chip_teal_old = """.chip--teal {
  background: var(--clr-secondary-light);
  color: var(--clr-primary);
}"""

chip_teal_new = """.chip--teal {
  background: linear-gradient(135deg, rgba(17, 202, 160, 0.15), rgba(123, 44, 191, 0.15));
  color: var(--clr-primary);
  border: 1px solid rgba(123, 44, 191, 0.2);
}"""

content = content.replace(chip_teal_old, chip_teal_new)

# 4. Update .section--alt
section_alt_old = """.section--alt {
  background: var(--clr-surface-alt);
}"""

section_alt_new = """.section--alt {
  background: radial-gradient(circle at top right, rgba(123, 44, 191, 0.03), transparent 40%),
              radial-gradient(circle at bottom left, rgba(255, 0, 110, 0.03), transparent 40%),
              var(--clr-surface-alt);
}"""

content = content.replace(section_alt_old, section_alt_new)

with open('/Users/ali/Documents/Academy/styles.css', 'w', encoding='utf-8') as f:
    f.write(content)
