---
name: persona-carousel
description: Build a persona-targeted, brand-researched carousel (mobile-friendly JPGs + flat PDF) tailored to a specific audience (investors, FBCs, sales, customers, internal team), goal (pitch, alignment, fundraising, launch), and company. Use whenever the user asks to "build a carousel", "create slides for X persona", "make a pitch carousel", or "build a deck for {company} for {audience}". The skill collects inputs, auto-researches the company logo + derives a palette, confirms a page outline before rendering, then produces 1080x1080 JPGs + a flat PDF.
---

# Persona Carousel Builder

Build a 3-4 page carousel tailored to a persona, goal, and company. The design system (cream background, Calibri typography, stamp-style cards with offset shadows, dark accent cards, pie chart, pipeline rows) stays locked across all carousels — only content, palette, and structure adapt to user input.

## When to invoke

- "Build a carousel for {persona/audience}"
- "Create a sales/investor/internal pitch deck"
- "Make a 4-page asset for {company} aimed at {audience}"
- "Build me a playbook/strategy carousel"

## Critical principle: confirm before rendering

Always show the user the logo + palette + page outline + draft copy and ask for approval before doing the final render. Palette extraction can be wrong. Copy might be off. Cheaper to fix in draft than in final JPGs.

## Step 1: Collect inputs (use AskUserQuestion + free-text follow-ups)

Gather these in a sensible flow. Start with the AskUserQuestion tool for structured choices, then use plain conversation for free-form inputs.

**Required (ask first, in batched AskUserQuestion):**

| Field | Type | Example |
| --- | --- | --- |
| **Persona** | choice + Other | Investment teams · FBCs / ops consultants · Sales engineers · Founders · Internal team · Other |
| **Goal** | choice + Other | Design partnership pitch · Sales asset · Internal alignment · Fundraising · Product launch · Other |
| **Page 4 type** | choice | Rollout plan · Product roadmap · Product proposal · Process/methodology · Skip Page 4 · Other (free text) |
| **Personal brand mode** | yes/no | Yes = include photo + name + email/phone/website on contact card |

**Required (ask as plain text questions, one at a time):**

1. **Company name?** — e.g., "Delightree", "Acme Capital"
2. **Company website URL?** — full URL like `https://delightree.com` or `https://app.example.io`. **Don't assume the URL is `companyname.com`** — different companies have different conventions (`.io`, `.ai`, `app.`, etc.). Always ask.
3. **Page 2 — what to feature?** Page 2 is the "playbook" page, fully customizable. The user picks what 4-6 items to feature:
   - Could be **AI agents** (e.g., Deal Brief, DD Diagnosis)
   - Could be **product modules** (e.g., Tasks, Audits, Training)
   - Could be **use cases** (e.g., Onboarding, Compliance, Growth)
   - Could be **services** offered (e.g., Strategy, Implementation)
   - Could be **anything else** the persona/goal calls for
   Ask: "What 4-6 items should Page 2 feature? For each: name + 1-line value description." Don't limit to "agents".
4. **Page 1 inputs (optional):** persona's "bridge role" between two entities (e.g., "investors sit between LPs and the market"). If not provided, draft from persona context.
5. **Personal brand details (only if user said yes):** name, email, phone (optional), personal URL (optional), photo file path.

**Page 4 specifics (depending on type chosen):**

- **Rollout plan** — 5 stages (e.g., "Discovery → Design → Prototype → Build → Ship"). Ask user to confirm or customize the stages and descriptions.
- **Product roadmap** — 5 horizons (e.g., Now / Q1 / Q2 / Q3 / Beyond) with focus areas. Ask user for the horizons and what's in each.
- **Product proposal** — 5 offerings/services with brief description. Ask user for the offerings.
- **Process/methodology** — 5 steps in the methodology + a guiding principle.
- **Custom** — 5 boxes the user defines in free text.

## Step 2: Research the company

Run the auto-research:

1. **Fetch the company website.** Use WebFetch on the URL the user gave.
2. **Find the logo.** Look for these in the HTML, in order of preference:
   - `<link rel="apple-touch-icon" href="...">` (often the cleanest icon, frequently SVG)
   - `<link rel="icon" type="image/svg+xml" href="...">`
   - `<meta property="og:image" content="...">`
   - `<link rel="shortcut icon" href="...">`
   - Footer `<img>` with alt containing "logo" or company name
3. **Download the logo** to `outputs/{company}-logo.{ext}`. SVG is best (vector, embedded easily). If only PNG/JPG available, use that.
4. **Derive the palette.** Run `scripts/extract_palette.py {logo_path}` which outputs 5 dominant colors as hex codes via PIL color quantization.
5. **Pick the role colors:**
   - **--ink** (text/dark): the darkest meaningful color from the palette (skip near-black if pure black; use deep blue/teal/etc.)
   - **--brand** (primary): the most saturated mid-tone (the company's "main" brand color)
   - **--warm** (warm accent): warmest hue if available; else use a complementary brown/gold/peach
   - **--bright** (accent / pop): brightest saturated color (used for the small "precious" pie slice and shadow accents)
   - **--bg** (background): warm cream / off-white / a desaturated tint of the lightest palette color
6. If extraction fails or the palette feels muddy, use the proven default Blue Jungle palette: `#011D4D / #034078 / #1282A2 / #E4DFDA / #63372C` and tell the user it's a fallback.

## Step 3: Draft & confirm

This is the gate. **Do not render until the user approves.**

Show the user:

1. **The logo** found (display it via the file the user can open).
2. **The 5-color palette** with hex codes and a 1-word role for each.
3. **Page outline** — for each page, the **draft headline** and a **1-line summary of the structure**. Example:

   > **Page 1 — Value chain:** "Investment team's operating brain." Bridge role (LPs ↔ portfolio) + time pie + 5-row question→agent→focus pipeline + outcomes + takeaway.
   > **Page 2 — Playbook:** "{custom title}." 5-6 cards: Deal Brief, DD Diagnosis, Portfolio Pulse, LP Memo, Market Brief, [+ optional dark feature card].
   > **Page 3 — Data layer:** "Powered by what you already see." Brain + 3 active streams + human layer + plug-ins.
   > **Page 4 — Rollout / Roadmap / Proposal:** "{title based on Page 4 type}." 5 stages/horizons/offerings + principle band + (optional) contact card.

4. Ask: **"Proceed with these, or want to swap palette / page count / a specific draft?"**

Iterate until the user says go.

## Step 4: Generate HTML

For each page, **read the matching reference file in `reference/`** as the structural template:

- `reference/page1-value-chain.html` — pie + pipeline structure
- `reference/page2-playbook.html` — N-card grid (handles 4, 5, or 6 items + optional dark feature card)
- `reference/page3-data-story.html` — brain + streams + human layer + plug-ins
- `reference/page4-flex.html` — flexible 5-stage layout (rollout / roadmap / proposal)

Substitute (do this in order):

1. **Color CSS variables** in `:root { ... }` to the derived palette
2. **Logo** in chrome (top-left): replace the `<svg>` block or `<img>` block with the company logo
3. **Page numbers**: update `01 / 04` etc. to match selected page count
4. **Headline + lead** with the approved drafts
5. **Body content** — pie segments, pipeline rows, playbook cards, data streams, plug-ins, page-4 stages
6. **Personal brand contact card** on Page 4 (only if personal brand mode is on)
7. **Photo** — substitute `<img src="tanishq.jpg">` with the user-supplied photo file path. Compress with PIL (`thumbnail((300,300))`, JPEG quality 86) before referencing it.

Save each rendered HTML to `outputs/carousel-page{N}.html`.

**Important content guidelines:**

- **Page 2 is fully flexible** — don't force "agents" or "intelligence" if the user chose products / modules / use cases. The card structure (number, name, value, icon) stays; the labels adapt.
- The **dark "always-on" / featured card** on Page 2 is **optional** — only include if the user has something that fits (e.g., an always-on monitoring layer, a featured offering, a hero capability). Otherwise just show 4-6 equal cards.
- **Page 4 is fully flexible** — same visual structure (5 stamp cards in a row, with the 5th often being the dark "finale"), but content can be rollout, roadmap, proposal, or custom. The user's choice in Step 1 dictates the labels.
- **Avoid em-dashes** (—) in the rendered copy. Use periods, commas, or colons instead. The user has explicitly asked for this.

## Step 5: Render

Run `scripts/render_carousel.py outputs/carousel-page{1..N}.html`:

The script:
1. Uses Playwright to open each HTML at 1080×1080 viewport
2. Screenshots `.slide` element as JPG (quality 88, 1x scale = mobile-friendly file size, ~130KB each)
3. Builds a flat-image PDF using ReportLab (each page is the JPG, ~700KB total — fast on mobile)
4. Optionally builds a vector PDF too via Playwright's `page.pdf()` for desktop sharing

Outputs:
- `outputs/{company}-carousel-page{1..N}.jpg` (individual JPGs for social posting)
- `outputs/{company}-carousel-mobile.pdf` (flat PDF, fast everywhere)
- `outputs/{company}-carousel-desktop.pdf` (vector PDF, optional)

## Step 6: Save and present

1. Copy outputs to the user's chosen folder (default: workspace folder).
2. Provide `computer://` links for each JPG and the PDFs.
3. Summarize what's in each page in a few sentences.

## Reference design system (locked)

Don't change these — they're the craft language of this carousel format:

- **Font**: `'Calibri', 'Carlito', 'Trebuchet MS', sans-serif`. Carlito imported from Google Fonts.
- **Background**: warm off-white (cream like `#E4DFDA` or `#F2EFE6`)
- **Cards (light)**: 1.5px solid ink border, 4px 4px 0 ink offset shadow, rounded 12-14px, padding 16-22px
- **Dark accent cards** (Intel, Brain, Goal band, Step 5 finale, Contact card): dark ink color (#011D4D or palette darkest) as bg, brand-color drop shadow (4px 4px 0)
- **Pie chart**: 230×230 donut, 60px inner hole, "INVESTOR / a typical week" centered text
- **Pipeline**: 3-column grid (1fr / 156px / 1fr), 5 rows, italic question text, solid bg skill chip with shadow, bold strategic focus text
- **Eyebrow**: small caps with letter-spacing 0.20em, uppercase, accent color, optional bar prefix
- **Spacing**: 60px outer padding, 16-22px inter-card gaps, 36px chrome padding

## Files in this skill

- `SKILL.md` — this file
- `reference/page1-value-chain.html` — Page 1 reference (investor version)
- `reference/page2-playbook.html` — Page 2 reference
- `reference/page3-data-story.html` — Page 3 reference
- `reference/page4-flex.html` — Page 4 reference (rollout structure)
- `scripts/extract_palette.py` — derive 5-color palette from logo via PIL color quantization
- `scripts/fetch_logo.py` — find and download company logo from a URL
- `scripts/render_carousel.py` — render HTML pages to JPG + flat PDF (+ optional vector PDF)

## Practical notes

- If `WebFetch` can't reach the company URL or the logo isn't findable, fall back to asking the user to upload the logo file directly. Don't block on auto-research.
- Always batch the render at the end, not per-page, so the user sees all 4 outputs at once.
- The **mobile-friendly flat PDF is the primary deliverable** — vector PDFs choke on mobile (gradients, drop shadows, SVG paths). The flat-image PDF opens instantly.
- Dimensions are 1080×1080 (square). Don't change unless user asks for another aspect ratio (e.g., 1080×1350 portrait for Instagram feed).
