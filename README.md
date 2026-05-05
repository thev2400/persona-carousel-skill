# persona-carousel

**On-brand, audience-specific carousels in 30 minutes. No designer required.**

A Claude skill that ships a publish-ready 4-page carousel for any audience. Drop in a persona, a goal, a company URL, and the content to feature — the skill researches the brand, locks in the palette, drafts the copy, confirms the plan, then outputs four 1080×1080 JPGs and a mobile-friendly flat PDF.

The design system (cream background, Calibri typography, stamp-style cards, signature pie chart, three-column pipeline, brain-and-streams data architecture) stays consistent across every deck. Only the colors, copy, and structure adapt to the brief.

## What gets built

| Page | Purpose |
| --- | --- |
| 1. Value chain | Persona's bridge role, time pie chart (manual / reactive / strategic), 5-row "question → agent → strategic focus" pipeline |
| 2. Playbook | 4–6 customizable cards — agents, products, modules, services, use cases — with optional dark "feature" card |
| 3. Data story | Central brain, three active data streams with integration logos, human-in-the-loop band, future plug-ins |
| 4. Flexible | Rollout plan / product roadmap / proposal / process — pick the layout, with optional personal contact card |

## Install

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/{USERNAME}/persona-carousel-skill ~/.claude/skills/persona-carousel
pip3 install --break-system-packages playwright Pillow reportlab pypdf
python3 -m playwright install chromium
```

Restart Claude Code. Invoke with `/persona-carousel` or by asking *"build a carousel for {audience} for {company}"*.

## Use without installing — share by prompt

If recipients can't install the skill locally, use the bootstrap prompt in [PROMPT.md](PROMPT.md). Anyone pasting it into a Claude session will have the skill fetched and run on the fly.

## How it works

1. **Asks** for persona, goal, company name, full website URL (always asks — no `companyname.com` assumption), Page 2 items, Page 4 type, personal-brand mode.
2. **Researches** the company website: pulls the cleanest logo (SVG preferred), derives a 5-color palette from logo fills or PIL median-cut quantization.
3. **Confirms** the logo, palette, page outline, and headlines before rendering.
4. **Adapts** the four reference HTML templates by swapping palette CSS variables, the logo, and all copy.
5. **Renders** with Playwright at 1080×1080, outputs JPGs and a flat-image PDF that opens instantly on mobile.

## Files

```
persona-carousel-skill/
├── SKILL.md                          # Instructions Claude follows
├── INSTALL.md                        # Local install + dependencies
├── PUBLISH.md                        # How to publish to GitHub
├── PROMPT.md                         # Shareable bootstrap prompt
├── README.md                         # This file
├── reference/
│   ├── page1-value-chain.html
│   ├── page2-playbook.html
│   ├── page3-data-story.html
│   └── page4-flex.html
└── scripts/
    ├── fetch_logo.py                 # Find + download company logo
    ├── extract_palette.py            # 5-color palette from logo
    └── render_carousel.py            # HTML → JPGs + flat PDF
```

## Built for

Marketing, sales, and founder teams that pitch multiple audiences without designer support.
