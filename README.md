# LVII Co-living — Waitlist site

Single-file static site (vanilla HTML/CSS/JS). No build step.

- `index.html` — the site (intro, story, questionnaire, waitlist)
- `apps-script.gs` — Google Apps Script that writes submissions to a Google Sheet

## Setup
1. Deploy `apps-script.gs` as a Google Apps Script web app (Execute as: Me, Access: Anyone).
2. Paste the web app URL into `CONFIG.endpoint` in `index.html`.
3. Host on any static host (GitHub Pages, Netlify, Vercel).
