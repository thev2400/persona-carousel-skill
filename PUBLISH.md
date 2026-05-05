# Publishing the persona-carousel skill to GitHub

You only need to do this once.

## Option A — via GitHub CLI (easiest)

```bash
cd ~/Claude_projects/Delightree-AI/persona-carousel-skill

# Initialize git
git init
git add .
git commit -m "Initial commit: persona-carousel skill"

# Create public repo and push
gh repo create persona-carousel-skill --public --source=. --push
```

You'll get a URL like `https://github.com/{your-username}/persona-carousel-skill`.

## Option B — via GitHub web

1. Create a new public repo at `https://github.com/new` named `persona-carousel-skill`.
2. From the local folder, push:

```bash
cd ~/Claude_projects/Delightree-AI/persona-carousel-skill
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/{your-username}/persona-carousel-skill.git
git push -u origin main
```

## Updating later

When you tweak the skill:

```bash
cd ~/Claude_projects/Delightree-AI/persona-carousel-skill
git add .
git commit -m "Tweak {what changed}"
git push
```

Anyone using the bootstrap prompt will fetch the latest `main` next time they invoke it.
