import os

# Update dashboard.css
with open('/Users/ali/Documents/Academy/dashboard.css', 'r', encoding='utf-8') as f:
    dashboard_css = f.read()

# 1. Dashboard card hover glow
dash_card_old = """.dash-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 80, 136, .1);
}"""

dash_card_new = """.dash-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(123, 44, 191, .15), 0 4px 12px rgba(17, 202, 160, .1);
}"""
dashboard_css = dashboard_css.replace(dash_card_old, dash_card_new)

# 2. Sidebar active states
sidebar_active_old = """.sidebar-link.active {
  background: var(--clr-primary-light);
  color: var(--clr-primary);
  font-weight: 700;
  border-right: 4px solid var(--clr-primary);
}"""

sidebar_active_new = """.sidebar-link.active {
  background: linear-gradient(90deg, var(--clr-primary-light), rgba(123, 44, 191, .05));
  color: var(--clr-primary);
  font-weight: 700;
  border-right: 4px solid var(--clr-purple);
}"""
dashboard_css = dashboard_css.replace(sidebar_active_old, sidebar_active_new)

with open('/Users/ali/Documents/Academy/dashboard.css', 'w', encoding='utf-8') as f:
    f.write(dashboard_css)


# Update checkout.css
with open('/Users/ali/Documents/Academy/checkout.css', 'r', encoding='utf-8') as f:
    checkout_css = f.read()

# Checkout plan glow
plan_old = """.plan-card--recommended {
  border: 2px solid var(--clr-primary);
  transform: scale(1.02);
  box-shadow: 0 16px 32px rgba(0, 80, 136, .12);
}"""

plan_new = """.plan-card--recommended {
  border: 2px solid var(--clr-purple);
  transform: scale(1.02);
  box-shadow: 0 16px 32px rgba(123, 44, 191, .2), 0 0 20px rgba(255, 0, 110, .1);
}"""
checkout_css = checkout_css.replace(plan_old, plan_new)

with open('/Users/ali/Documents/Academy/checkout.css', 'w', encoding='utf-8') as f:
    f.write(checkout_css)


# Update lms.css
with open('/Users/ali/Documents/Academy/lms.css', 'r', encoding='utf-8') as f:
    lms_css = f.read()

# Active video state
video_active_old = """.video-item.active {
  background: var(--clr-primary-light);
  border-left: 4px solid var(--clr-primary);
}"""

video_active_new = """.video-item.active {
  background: linear-gradient(90deg, var(--clr-primary-light), rgba(255, 0, 110, .05));
  border-left: 4px solid var(--clr-pink);
}"""
lms_css = lms_css.replace(video_active_old, video_active_new)

with open('/Users/ali/Documents/Academy/lms.css', 'w', encoding='utf-8') as f:
    f.write(lms_css)


# Update auth.css
with open('/Users/ali/Documents/Academy/auth.css', 'r', encoding='utf-8') as f:
    auth_css = f.read()

# Auth box glow
auth_box_old = """.auth-box {
  background: var(--clr-white);
  padding: var(--sp-8);
  border-radius: var(--radius-xl);
  box-shadow: 0 16px 48px rgba(0, 80, 136, .08);
  width: 100%;
  max-width: 440px;
}"""

auth_box_new = """.auth-box {
  background: var(--clr-white);
  padding: var(--sp-8);
  border-radius: var(--radius-xl);
  box-shadow: 0 16px 48px rgba(123, 44, 191, .15), 0 0 24px rgba(17, 202, 160, .1);
  width: 100%;
  max-width: 440px;
}"""
auth_css = auth_css.replace(auth_box_old, auth_box_new)

with open('/Users/ali/Documents/Academy/auth.css', 'w', encoding='utf-8') as f:
    f.write(auth_css)
