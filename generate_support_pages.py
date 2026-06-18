import os
import re

directory = '/Users/ali/Documents/Academy'

# 1. Read index.html to extract header and footer templates
with open(os.path.join(directory, 'index.html'), 'r') as f:
    index_content = f.read()

# Extract header: from start to </header>
header_match = re.search(r'(<!DOCTYPE html>.*?</header>)', index_content, re.DOTALL)
if header_match:
    header_html = header_match.group(1)
else:
    print("Could not extract header")
    exit(1)

# Extract footer: from <footer class="footer"> to end
footer_match = re.search(r'(<footer class="footer">.*</html>)', index_content, re.DOTALL)
if footer_match:
    footer_html = footer_match.group(1)
else:
    print("Could not extract footer")
    exit(1)

# 2. Define the old support links block and new support links block
old_support_links = """        <ul>
          <li><a href="javascript:void(0)" onclick="alert(`Coming Soon!`)">Privacy Policy</a></li>
          <li><a href="javascript:void(0)" onclick="alert(`Coming Soon!`)">Terms of Service</a></li>
          <li><a href="javascript:void(0)" onclick="alert(`Coming Soon!`)">Refund Policy</a></li>
          <li><a href="javascript:void(0)" onclick="alert(`Coming Soon!`)">Cookie Policy</a></li>
          <li><a href="javascript:void(0)" onclick="alert(`Coming Soon!`)">Security</a></li>
        </ul>"""

new_support_links = """        <ul>
          <li><a href="privacy.html">Privacy Policy</a></li>
          <li><a href="terms.html">Terms of Service</a></li>
          <li><a href="refund.html">Refund Policy</a></li>
          <li><a href="cookie.html">Cookie Policy</a></li>
          <li><a href="security.html">Security</a></li>
        </ul>"""

# Update footer_html with new links
footer_html = footer_html.replace(old_support_links, new_support_links)

# 3. Create the 5 pages
pages = {
    'privacy.html': {
        'title': 'Privacy Policy',
        'content': """
<section class="legal-section">
<h3 class="legal-heading">1. Introduction</h3>
<p class="legal-body">Athenaeum is committed to protecting your privacy. This policy explains what data we collect and how we use it.</p>
</section>

<section class="legal-section">
<h3 class="legal-heading">2. Information We Collect</h3>
<ul class="legal-body">
  <li>Name and email address at registration</li>
  <li>Learning progress and exam results</li>
  <li>Usage data to improve the platform</li>
  <li>Payment information (processed securely by Stripe and JazzCash — we never store card details)</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">3. How We Use Your Information</h3>
<ul class="legal-body">
  <li>To provide and personalize your learning experience</li>
  <li>To track your progress and award XP</li>
  <li>To send important account notifications</li>
  <li>To improve Athenaeum's features and content</li>
  <li>We never sell your data to third parties</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">4. Data Storage & Security</h3>
<ul class="legal-body">
  <li>All data is stored securely on Supabase</li>
  <li>Passwords are encrypted and never visible</li>
  <li>We use SSL encryption across the platform</li>
  <li>You can request deletion of your account and data at any time</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">5. Cookies</h3>
<ul class="legal-body">
  <li>We use essential cookies for authentication</li>
  <li>No advertising or tracking cookies</li>
  <li>You can clear cookies in your browser settings</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">6. Children's Privacy</h3>
<ul class="legal-body">
  <li>Athenaeum is designed for students of all ages</li>
  <li>We encourage parental involvement</li>
  <li>Parents can monitor progress via Parent Dashboard</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">7. Contact Us</h3>
<p class="legal-body">If you have any questions about this policy, contact us at: support@athenaeumacademy.com</p>
</section>
"""
    },
    'terms.html': {
        'title': 'Terms of Service',
        'content': """
<section class="legal-section">
<h3 class="legal-heading">1. Acceptance of Terms</h3>
<p class="legal-body">By creating an account on Athenaeum, you agree to these Terms of Service. Please read them carefully before using the platform.</p>
</section>

<section class="legal-section">
<h3 class="legal-heading">2. Account Responsibilities</h3>
<ul class="legal-body">
  <li>You must provide accurate information during registration</li>
  <li>You are responsible for keeping your password secure</li>
  <li>One account per student — sharing accounts is not permitted</li>
  <li>You must be at least 10 years old to create an account</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">3. Free Trial</h3>
<ul class="legal-body">
  <li>New students receive a 3-day free trial</li>
  <li>Free trial includes limited Athenaeum Assistant access (5 questions per day)</li>
  <li>Free trial includes limited mock exams (2 per day)</li>
  <li>Trial expires automatically after 72 hours</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">4. Paid Subscription</h3>
<ul class="legal-body">
  <li>Paid plans unlock unlimited access to all features</li>
  <li>Subscriptions are billed as per selected plan</li>
  <li>Payments processed via Stripe (international) and JazzCash (Pakistan)</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">5. Acceptable Use</h3>
<ul class="legal-body">
  <li>Do not share course content outside the platform</li>
  <li>Do not attempt to bypass trial or payment limits</li>
  <li>Do not misuse Athenaeum Assistant for non-academic purposes</li>
  <li>Respectful behavior is expected at all times</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">6. Intellectual Property</h3>
<ul class="legal-body">
  <li>All course content is owned by Athenaeum</li>
  <li>Athenaeum Assistant responses are for personal learning only</li>
  <li>You may not reproduce or distribute any content</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">7. Termination</h3>
<p class="legal-body">We reserve the right to suspend or terminate accounts that violate these terms without notice.</p>
</section>

<section class="legal-section">
<h3 class="legal-heading">8. Contact Us</h3>
<p class="legal-body">Questions about our terms?<br>Email: support@athenaeumacademy.com</p>
</section>
"""
    },
    'refund.html': {
        'title': 'Refund Policy',
        'content': """
<section class="legal-section">
<h3 class="legal-heading">1. Our Commitment</h3>
<p class="legal-body">We want every student to be completely satisfied with Athenaeum. If you are not happy, we are here to help.</p>
</section>

<section class="legal-section">
<h3 class="legal-heading">2. Free Trial</h3>
<p class="legal-body">Athenaeum offers a 3-day free trial so you can explore the platform before making any payment. We encourage you to use it fully.</p>
</section>

<section class="legal-section">
<h3 class="legal-heading">3. Refund Eligibility</h3>
<ul class="legal-body">
  <li>Refund requests made within 7 days of payment are eligible for a full refund</li>
  <li>Requests after 7 days are reviewed case by case</li>
  <li>Refunds are not available if more than 50% of course content has been accessed</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">4. How to Request a Refund</h3>
<ul class="legal-body">
  <li>Email us at: support@athenaeumacademy.com</li>
  <li>Include your registered email and reason for refund</li>
  <li>We will respond within 2 business days</li>
  <li>Approved refunds are processed within 5-7 business days</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">5. Non-Refundable Situations</h3>
<ul class="legal-body">
  <li>Accounts suspended for Terms of Service violations</li>
  <li>Requests made after 7 days with significant usage</li>
  <li>JazzCash payments may have different processing timelines</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">6. Contact Us</h3>
<p class="legal-body">For refund requests or questions:<br>support@athenaeumacademy.com</p>
</section>
"""
    },
    'cookie.html': {
        'title': 'Cookie Policy',
        'content': """
<section class="legal-section">
<h3 class="legal-heading">1. What Are Cookies</h3>
<p class="legal-body">Cookies are small text files stored on your device when you visit a website. They help us remember your preferences and keep you logged in.</p>
</section>

<section class="legal-section">
<h3 class="legal-heading">2. Cookies We Use</h3>
<p class="legal-body"><strong>Essential Cookies:</strong></p>
<ul class="legal-body">
  <li>Authentication: keeps you logged in securely</li>
  <li>Session: remembers your current activity</li>
  <li>Preferences: saves your settings</li>
</ul>
<p class="legal-body" style="margin-top:10px;"><strong>We do NOT use:</strong></p>
<ul class="legal-body">
  <li>Advertising cookies</li>
  <li>Third-party tracking cookies</li>
  <li>Social media tracking pixels</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">3. How Long Cookies Last</h3>
<ul class="legal-body">
  <li>Session cookies: deleted when you close browser</li>
  <li>Authentication cookies: last 30 days (if Remember Me is selected)</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">4. Managing Cookies</h3>
<p class="legal-body">You can clear or disable cookies in your browser settings at any time. Note that disabling cookies will log you out of Athenaeum.</p>
</section>

<section class="legal-section">
<h3 class="legal-heading">5. Contact Us</h3>
<p class="legal-body">Questions about cookies?<br>Email: support@athenaeumacademy.com</p>
</section>
"""
    },
    'security.html': {
        'title': 'Security',
        'content': """
<section class="legal-section">
<h3 class="legal-heading">1. Our Security Commitment</h3>
<p class="legal-body">At Athenaeum, the security of your personal data and learning information is our top priority. We use industry-standard security practices throughout the platform.</p>
</section>

<section class="legal-section">
<h3 class="legal-heading">2. Data Encryption</h3>
<ul class="legal-body">
  <li>All data is transmitted over HTTPS/SSL</li>
  <li>Passwords are hashed and never stored in plain text</li>
  <li>Supabase provides enterprise-grade database security</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">3. Authentication Security</h3>
<ul class="legal-body">
  <li>Email and password login with encryption</li>
  <li>Google OAuth for secure social login</li>
  <li>Passkey support for passwordless login</li>
  <li>Role-based access control: Students, Teachers, Parents, and Admins each have separate secured access</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">4. Payment Security</h3>
<ul class="legal-body">
  <li>Payments are processed by Stripe and JazzCash</li>
  <li>We never store credit card details</li>
  <li>All payment data is PCI-DSS compliant</li>
  <li>Transactions are encrypted end-to-end</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">5. Account Protection</h3>
<ul class="legal-body">
  <li>Automatic logout after inactivity</li>
  <li>Suspicious login detection</li>
  <li>Password reset via verified email only</li>
  <li>hCaptcha on login to prevent bots</li>
</ul>
</section>

<section class="legal-section">
<h3 class="legal-heading">6. Reporting a Security Issue</h3>
<p class="legal-body">If you discover a security vulnerability, please report it responsibly:<br>Email: support@athenaeumacademy.com<br>We take all security reports seriously and respond within 24 hours.</p>
</section>
"""
    }
}

css_block = """
<style>
  .legal-container {
    max-width: 760px;
    margin: 80px auto 100px;
    padding: 0 20px;
  }
  .legal-page-title {
    font-family: 'Merriweather', serif;
    font-size: 32px;
    font-weight: 900;
    color: #005088;
    margin-bottom: 8px;
    line-height: 1.2;
  }
  .legal-date {
    font-family: 'Urbanist', sans-serif;
    font-size: 14px;
    color: #64748B;
    margin-bottom: 40px;
    padding-bottom: 24px;
    border-bottom: 1px solid #E2E8F0;
  }
  .legal-section {
    margin-bottom: 28px;
  }
  .legal-heading {
    font-family: 'Merriweather', serif;
    font-size: 18px;
    font-weight: 700;
    color: #005088;
    margin-bottom: 12px;
    line-height: 1.4;
  }
  .legal-body {
    font-family: 'Urbanist', sans-serif;
    font-size: 15px;
    line-height: 1.7;
    color: #333;
    margin: 0;
  }
  ul.legal-body {
    padding-left: 20px;
    margin-top: 8px;
  }
  ul.legal-body li {
    margin-bottom: 8px;
  }
  ul.legal-body li:last-child {
    margin-bottom: 0;
  }
</style>
"""

# For the 5 new pages
for filename, page_data in pages.items():
    page_html = header_html + css_block + f"""
<main class="legal-container">
  <h1 class="legal-page-title">{page_data['title']}</h1>
  <div class="legal-date">Last Updated: June 2026</div>
  {page_data['content']}
</main>
""" + footer_html

    with open(os.path.join(directory, filename), 'w') as f:
        f.write(page_html)
    print(f"Created {filename}")

# 4. Update the Support links in all existing .html files
for fname in os.listdir(directory):
    if fname.endswith('.html') and fname not in pages.keys():
        fpath = os.path.join(directory, fname)
        with open(fpath, 'r') as f:
            content = f.read()
        
        if old_support_links in content:
            content = content.replace(old_support_links, new_support_links)
            with open(fpath, 'w') as f:
                f.write(content)
            print(f"Updated footer in {fname}")
