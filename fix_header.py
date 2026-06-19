import os
import glob
import re

html_files = glob.glob('*.html')

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # 1. Replace Cart with Notifications
    if 'shopping_cart' in content:
        content = content.replace(
            '<button class="icon-btn cart-btn" aria-label="Cart" id="btn-cart">',
            '<button class="icon-btn cart-btn" aria-label="Notifications" id="btn-notifications">'
        )
        content = content.replace(
            '<button class="icon-btn" aria-label="Cart" id="btn-cart">',
            '<button class="icon-btn" aria-label="Notifications" id="btn-notifications">'
        )
        content = content.replace(
            '<span class="material-symbols-outlined">shopping_cart</span>',
            '<span class="material-symbols-outlined">notifications</span>'
        )
        modified = True
        
    # 2. Fix Academics Alignment
    academics_old = '<a href="javascript:void(0)" class="nav-link has-dropdown" style="display:inline-flex; align-items:center; gap:4px;">Academics <span class="material-symbols-outlined" style="font-size:18px;">keyboard_arrow_down</span></a>'
    academics_new = '<a href="javascript:void(0)" class="nav-link has-dropdown">Academics <span class="material-symbols-outlined" style="font-size:18px; vertical-align:middle; margin-top:-3px;">keyboard_arrow_down</span></a>'
    
    if academics_old in content:
        content = content.replace(academics_old, academics_new)
        modified = True
        
    # 3. Add Search Overlay if not present, right before </nav>
    search_overlay = '''
      <!-- Search Overlay -->
      <div class="search-overlay" id="search-overlay" style="display: none; position: absolute; top: 100%; left: 0; width: 100%; background: var(--clr-surface); padding: 1rem 24px; border-bottom: 1px solid var(--clr-border); box-shadow: var(--shadow-md); z-index: 999;">
        <div style="max-width: 800px; margin: 0 auto; display: flex; gap: 10px;">
          <input type="text" id="global-search-input" placeholder="Search courses, skills, and resources..." style="flex: 1; padding: 0.8rem 1.2rem; border: 1px solid var(--clr-border); border-radius: var(--radius-full); font-size: 1rem; outline: none;">
          <button class="btn btn-primary" onclick="executeGlobalSearch()">Search</button>
        </div>
      </div>
'''
    if 'id="search-overlay"' not in content and 'id="btn-search"' in content:
        if '    </nav>' in content:
            content = content.replace('    </nav>', search_overlay + '    </nav>')
            modified = True
            
    if modified:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {file}")

print("Done updating HTML files.")
