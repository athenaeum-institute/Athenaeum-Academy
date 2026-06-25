import os
import glob

DOMAIN = "athenaeumacademy.com"
PRIVATE_PAGES = {
    "auth.html",
    "admin.html",
    "dashboard-student.html",
    "dashboard-parent.html",
    "dashboard-teacher.html",
}

PUBLIC_META = """
  <!-- EAT Trust Signals -->
  <meta name="author" content="Athenaeum Academy">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://{domain}/{filename}">
"""

PRIVATE_META = """
  <!-- EAT Trust Signals (Private) -->
  <meta name="robots" content="noindex, nofollow">
"""

JSON_LD_1 = """
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"EducationalOrganization","name":"Athenaeum Academy","url":"https://athenaeumacademy.com","description":"Pakistan's leading online academy for O Levels, A Levels, Matric, Intermediate, MDCAT and ECAT preparation.","address":{"@type":"PostalAddress","addressLocality":"Lahore","addressCountry":"PK"},"contactPoint":{"@type":"ContactPoint","telephone":"+92-328-6715408","contactType":"customer support","availableLanguage":["English","Urdu"]},"areaServed":{"@type":"Country","name":"Pakistan"}}
  </script>
"""

JSON_LD_2 = """
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"What courses does Athenaeum offer?","acceptedAnswer":{"@type":"Answer","text":"Athenaeum offers online courses for O Levels, A Levels, Matric Science, FSc, MDCAT and ECAT with live classes and expert Pakistani teachers."}},{"@type":"Question","name":"How much do Athenaeum courses cost?","acceptedAnswer":{"@type":"Answer","text":"Courses start from Rs 2,999. Free trial available. Payment via JazzCash, Easypaisa, Bank Transfer, Visa or Mastercard."}},{"@type":"Question","name":"Can parents track their child's progress?","acceptedAnswer":{"@type":"Answer","text":"Yes, Athenaeum has a dedicated Parent Dashboard for real-time tracking of progress, scores and attendance."}}]}
  </script>
"""

html_files = glob.glob("*.html")

for filepath in html_files:
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already added
    if "Athenaeum Academy" in content and "robots" in content and ("canonical" in content or "noindex" in content):
        if not filename == "index.html" or "EducationalOrganization" in content:
            continue

    # Determine tags
    if filename in PRIVATE_PAGES:
        tags = PRIVATE_META
    else:
        # Avoid double slash if index
        if filename == "index.html":
            tags = PUBLIC_META.format(domain=DOMAIN, filename="")
        else:
            tags = PUBLIC_META.format(domain=DOMAIN, filename=filename)

    # Insert into <head>
    head_end_idx = content.find("</head>")
    if head_end_idx == -1:
        continue

    # For index.html, also add JSON-LD
    insertion = tags
    if filename == "index.html":
        if "EducationalOrganization" not in content:
            insertion += JSON_LD_1
        if "FAQPage" not in content:
            insertion += JSON_LD_2

    new_content = content[:head_end_idx] + insertion + content[head_end_idx:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

print(f"Processed {len(html_files)} HTML files.")

# Create humans.txt
with open("humans.txt", "w", encoding="utf-8") as f:
    f.write('''/* TEAM */
Organization: Athenaeum Academy
Location: Lahore, Pakistan
Contact: support@athenaeumacademy.com
''')
print("Created humans.txt")
