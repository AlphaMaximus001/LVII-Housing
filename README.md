# LVII Co-living — Waitlist site

Single-file static site (vanilla HTML/CSS/JS). No build step.

- `index.html` — the site (intro, story, questionnaire, waitlist)
- `apps-script.gs` — Google Apps Script that writes submissions to a Google Sheet
- `assets/` — images (pine photo)
- `vercel.json` — Vercel headers/caching

## Setup
1. Deploy `apps-script.gs` as a Google Apps Script web app (Execute as: Me, Access: Anyone).
2. Paste the web app URL into `CONFIG.endpoint` in `index.html`.
3. Import the repo in Vercel (Framework preset: Other, no build command). Pushes to `main` deploy automatically.

When you change `apps-script.gs`, redeploy it via Manage deployments → Edit → New version so the URL stays the same.
