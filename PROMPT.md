# Persona Carousel — shareable prompt

Replace `{USERNAME}` (and `{REPO}` if you renamed it) with your GitHub handle.
Then paste the block below to anyone using Claude — Claude Code, Claude Desktop, or Cowork mode. It bootstraps everything from the public repo.

---

```
Build a persona-targeted carousel using the skill published at:
  https://github.com/{USERNAME}/persona-carousel-skill

## Bootstrap (idempotent — safe to re-run)

If /tmp/persona-carousel-skill/SKILL.md doesn't already exist, run:

```bash
mkdir -p /tmp/persona-carousel-skill
curl -sL https://github.com/{USERNAME}/persona-carousel-skill/archive/refs/heads/main.tar.gz \
  | tar xz -C /tmp/persona-carousel-skill --strip-components=1
```

Then ensure dependencies (one-off per machine, idempotent):

```bash
pip3 install --break-system-packages -q playwright Pillow reportlab pypdf
python3 -m playwright install chromium
```

## Workflow

Read /tmp/persona-carousel-skill/SKILL.md and follow its workflow exactly.

In short: ask me for persona, goal, company name, full company URL, the 4-6 things to feature on Page 2 (agents, products, modules, services, use cases — whatever fits), Page 4 type (rollout / roadmap / proposal / process / custom / skip), and whether to include a personal contact card.

Auto-research the company logo and 5-color palette using the included scripts (scripts/fetch_logo.py and scripts/extract_palette.py). Confirm the plan with me before rendering.

Output: four 1080×1080 JPGs and a flat-image PDF saved to my chosen workspace folder.
```

---

## What the recipient does

Paste the block above into any Claude session. Claude will:

1. Fetch the skill files from your GitHub repo into `/tmp/persona-carousel-skill/`
2. Install the Python dependencies (playwright, Pillow, reportlab, pypdf)
3. Read SKILL.md and run the full workflow

If you push updates to GitHub, anyone re-running the prompt picks them up automatically.
