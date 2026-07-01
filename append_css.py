import os
css = """

/* --- MOBILE RESPONSIVE FIXES (ADDED FOR MOBILE ONLY) --- */
@media (max-width: 768px) {
  /* Fix hero image taking too much space */
  .hero-img-3d {
    max-width: 250px !important;
    height: auto !important;
    margin: 0 auto !important;
    display: block !important;
  }
  
  .hero-visual {
    margin-bottom: -40px !important;
    text-align: center;
  }

  /* Fix welcome back text squishing */
  .hero-title {
    font-size: 2rem !important;
    line-height: 1.3 !important;
  }

  .hero-title span[style*="font-size: 24px"] {
    font-size: 1.3rem !important;
    line-height: 1.4 !important;
    white-space: normal !important;
    display: block !important;
    margin-top: 5px !important;
  }

  /* Fix feature grid wrapping weirdly */
  .feature-bar .feature-grid {
    grid-template-columns: 1fr 1fr !important;
    gap: 15px 5px !important;
    padding: 10px 10px !important;
  }

  .feature-item {
    font-size: 0.8rem !important;
    align-items: center !important;
    text-align: left !important;
    justify-content: flex-start;
  }

  /* Fix floating assistant badge in about section overflowing */
  .ustad-floating-badge, .about-badge {
    transform: scale(0.7) !important;
    transform-origin: left bottom !important;
    left: 5px !important;
    bottom: 5px !important;
    max-width: 280px !important;
  }
  
  /* Fix the right-side positioning if it overflows */
  .experience-block {
    transform: scale(0.7) !important;
    transform-origin: right bottom !important;
    right: 5px !important;
    bottom: 5px !important;
  }

  /* Prevent body overflow */
  body {
    overflow-x: hidden !important;
  }
}
"""

with open('e:/Academy/styles.css', 'a', encoding='utf-8') as f:
    f.write(css)
print('Appended CSS to styles.css')
