import re

with open('styles.css', 'r') as f:
    content = f.read()

# Make the cards much more compact
replacements = [
    (r'\.course-thumb {\n  position: relative;\n  overflow: hidden;\n  height: 150px;\n}', 
     '.course-thumb {\n  position: relative;\n  overflow: hidden;\n  height: 120px;\n}'),
    
    (r'\.course-body {\n  padding: 1\.2rem;\n  display: flex;\n  flex-direction: column;\n  flex: 1;\n}',
     '.course-body {\n  padding: 1rem;\n  display: flex;\n  flex-direction: column;\n  flex: 1;\n}'),
     
    (r'\.course-title {\n  font-size: 1\.1rem;\n  font-weight: 700;\n  color: var\(--clr-text\);\n  margin-bottom: 0\.5rem;\n',
     '.course-title {\n  font-size: 1rem;\n  font-weight: 700;\n  color: var(--clr-text);\n  margin-bottom: 0.3rem;\n'),
     
    (r'\.course-meta {\n  display: flex;\n  gap: 1rem;\n  font-size: 0\.85rem;\n  color: var\(--clr-text-muted\);\n  margin-bottom: auto;\n}',
     '.course-meta {\n  display: flex;\n  gap: 0.5rem;\n  font-size: 0.8rem;\n  color: var(--clr-text-muted);\n  margin-bottom: auto;\n}'),
     
    (r'\.course-footer {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  padding-top: 1rem;\n  margin-top: 1rem;\n  border-top: 1px solid rgba\(0,0,0,0\.06\);\n}',
     '.course-footer {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  padding-top: 0.8rem;\n  margin-top: 0.8rem;\n  border-top: 1px solid rgba(0,0,0,0.06);\n}'),
     
    (r'\.course-price {\n  font-family: var\(--font-heading\);\n  font-size: 1\.25rem;\n  font-weight: 800;\n  color: var\(--clr-primary\);\n}',
     '.course-price {\n  font-family: var(--font-heading);\n  font-size: 1.1rem;\n  font-weight: 800;\n  color: var(--clr-primary);\n}'),
     
    (r'\.course-card-btn {\n  margin: 0 1\.2rem 1\.2rem 1\.2rem;\n  padding: 0\.7rem;\n  border-radius: 8px;\n  text-align: center;\n  font-weight: 600;\n  font-size: 0\.95rem;\n  background: var\(--clr-primary\);\n  color: white;\n  transition: all 0\.2s ease;\n  text-decoration: none;\n}',
     '.course-card-btn {\n  margin: 0 1rem 1rem 1rem;\n  padding: 0.55rem;\n  border-radius: 8px;\n  text-align: center;\n  font-weight: 600;\n  font-size: 0.85rem;\n  background: var(--clr-primary);\n  color: white;\n  transition: all 0.2s ease;\n  text-decoration: none;\n}'),
     
    (r'\.courses-catalog-grid {\n  display: grid;\n  grid-template-columns: repeat\(auto-fill, minmax\(260px, 1fr\)\);\n  gap: 1\.5rem;\n  margin-bottom: var\(--sp-12\);\n}',
     '.courses-catalog-grid {\n  display: grid;\n  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));\n  gap: 1.25rem;\n  margin-bottom: var(--sp-12);\n}'),
     
    (r'\.courses-scroll-container \.course-card {\n  flex: 0 0 280px; \n}',
     '.courses-scroll-container .course-card {\n  flex: 0 0 250px; \n}')
]

for old_str, new_str in replacements:
    content = re.sub(old_str, new_str, content)

with open('styles.css', 'w') as f:
    f.write(content)

