# Installing the persona-carousel skill

## Option 1 — Claude Code (personal skill)

```bash
mkdir -p ~/.claude/skills
cp -r /Users/tanishq/Claude_projects/Delightree-AI/persona-carousel-skill ~/.claude/skills/persona-carousel
```

Restart Claude Code. Invoke with `/persona-carousel` or by asking "build a carousel for [audience] for [company]".

## Option 2 — Cowork mode

Place the folder under your Cowork plugins skills directory (path varies by version). The skill auto-loads on next session start.

## Dependencies

Once-off setup on the machine that runs the skill:

```bash
pip3 install --break-system-packages playwright Pillow reportlab pypdf
python3 -m playwright install chromium
```

## Quick test (no Claude needed)

Verify the helper scripts work:

```bash
# Fetch Delightree's logo
python3 scripts/fetch_logo.py https://delightree.com /tmp/dt
# → /tmp/dt/logo.svg

# Extract its palette
python3 scripts/extract_palette.py /tmp/dt/logo.svg
# → #947AFF, #E9E4FF, #33313F, #FFDD00, #BFF3E6

# Render carousel pages (uses the bundled investor pages as a smoke test)
python3 scripts/render_carousel.py investor-test reference/page1-value-chain.html reference/page2-playbook.html reference/page3-data-story.html reference/page4-flex.html
# → investor-test-page{1..4}.jpg + investor-test-mobile.pdf next to the HTML files
```

## What the skill does, end-to-end

1. **Asks** for persona, goal, company name, company URL, page-2 items (4-6 anything — agents, products, modules, services, use cases), page-4 type (rollout / roadmap / proposal / process / custom / skip), and personal-brand mode (optional photo + contact).
2. **Researches** the company website: pulls the cleanest available logo (prefers SVG → apple-touch-icon → og:image → footer img), extracts a 5-color palette via PIL median-cut quantization (or direct SVG fill parsing).
3. **Confirms with you**: shows the logo, the palette with hex codes, the page outline, and draft headlines. Waits for your approval before rendering.
4. **Generates HTML** by adapting the four `reference/` templates: swaps in the palette, the logo, the company-/persona-specific copy, the customizable page-2 cards, and the chosen page-4 layout.
5. **Renders** to four 1080×1080 JPGs (~130 KB each) and a flat-image PDF (~700 KB total). Optionally also a vector PDF for desktop.

The flat-image PDF is the recommended deliverable — opens instantly on mobile, no SVG/gradient rendering pain.
