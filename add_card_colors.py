import os

with open('/Users/ali/Documents/Academy/styles.css', 'a', encoding='utf-8') as f:
    f.write('''

/* ── DYNAMIC EDUCATION COLORS FOR CARDS ── */
/* O/A Level Cards */
.oa-card:nth-child(4n+1) .oa-card-icon { background: rgba(255, 152, 0, 0.15); color: #FF9800; }
.oa-card:nth-child(4n+1):hover { border-color: #FF9800; box-shadow: 0 12px 32px rgba(255, 152, 0, 0.15); }

.oa-card:nth-child(4n+2) .oa-card-icon { background: rgba(3, 169, 244, 0.15); color: #03A9F4; }
.oa-card:nth-child(4n+2):hover { border-color: #03A9F4; box-shadow: 0 12px 32px rgba(3, 169, 244, 0.15); }

.oa-card:nth-child(4n+3) .oa-card-icon { background: rgba(103, 58, 183, 0.15); color: #673AB7; }
.oa-card:nth-child(4n+3):hover { border-color: #673AB7; box-shadow: 0 12px 32px rgba(103, 58, 183, 0.15); }

.oa-card:nth-child(4n+4) .oa-card-icon { background: rgba(76, 175, 80, 0.15); color: #4CAF50; }
.oa-card:nth-child(4n+4):hover { border-color: #4CAF50; box-shadow: 0 12px 32px rgba(76, 175, 80, 0.15); }

/* Matric / Inter Cards */
.matric-card:nth-child(4n+1) .matric-icon { color: #FF9800; }
.matric-card:nth-child(4n+1)::before { background: linear-gradient(90deg, #FF9800, #FFC107); }
.matric-card:nth-child(4n+1):hover { border-color: #FF9800; box-shadow: 0 12px 32px rgba(255, 152, 0, 0.15); }

.matric-card:nth-child(4n+2) .matric-icon { color: #4CAF50; }
.matric-card:nth-child(4n+2)::before { background: linear-gradient(90deg, #4CAF50, #8BC34A); }
.matric-card:nth-child(4n+2):hover { border-color: #4CAF50; box-shadow: 0 12px 32px rgba(76, 175, 80, 0.15); }

.matric-card:nth-child(4n+3) .matric-icon { color: #E91E63; }
.matric-card:nth-child(4n+3)::before { background: linear-gradient(90deg, #E91E63, #9C27B0); }
.matric-card:nth-child(4n+3):hover { border-color: #E91E63; box-shadow: 0 12px 32px rgba(233, 30, 99, 0.15); }

.matric-card:nth-child(4n+4) .matric-icon { color: #03A9F4; }
.matric-card:nth-child(4n+4)::before { background: linear-gradient(90deg, #03A9F4, #00BCD4); }
.matric-card:nth-child(4n+4):hover { border-color: #03A9F4; box-shadow: 0 12px 32px rgba(3, 169, 244, 0.15); }
''')
