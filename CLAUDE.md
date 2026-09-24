# LVII Co-living — Project Handoff

## The venture
LVII Co-living ("Co-living, Redefined"), a Maaef Group venture starting in Lucknow; don't tie copy to one neighbourhood because expansion is planned. We lease premium flats from owners, renovate them, and re-lease them to tenants. Tenants pay monthly rent plus their share of electricity. Meals, cleaning, laundry, staff and repairs are included and managed by us.

## The site's job
A waitlist and validation site. Flow: intro animation → story "video" (animated in-page) → 8-question survey → waitlist form. The goal is to collect data on who is actually interested.

## Tech
- A single `index.html`: vanilla HTML/CSS/JS, no framework, no build step.
- Google Fonts: Tinos (all serif), Onest (sans).
- The pine photo lives in `assets/pine.jpg` (preloaded; the intro waits up to 2.5s for it to decode). The logo SVG path is inline.
- `apps-script.gs` is a Google Apps Script web app that appends each submission to a Google Sheet. Its URL goes in `CONFIG.endpoint` in `index.html`, which is currently empty, so nothing is saved yet. The form POSTs with `no-cors`, so the page can't read the response.
- Spam: a hidden honeypot field (`#company`). If it's filled, the page shows success but sends nothing, and the Apps Script also drops the row.
- Hosting: Vercel, static, no build. `vercel.json` sets clean URLs and caches `/assets/*` for 30 days, so rename an asset when you replace it.

## Brand
- Colors: green `#065442` (primary), deep `#032E24`, black `#000`, white `#FFF`, mist `#EEF3F0`, lamp accent `#F2B544`.
- Logo mark: a traced SVG (`<symbol id="mark">`, viewBox `0 0 138 158.5`), slightly faceted because it came from a low-res screenshot. Replace it with a vector from the original Canva PNGs.
- Header lockup: mark + "LVII" + "Co-living / REDEFINED". The footer matches.

## Intro sequence (about 6.5s, skippable, respects reduced motion)
1. Pine image, no fog or rain, with a crisp white "LVII" (Tinos 700) centred.
2. White bars drop in from the top and bottom, with scrolling "LVII" strips (top moves left→right, bottom right→left).
3. The bars retract and the screen washes to solid green.
4. The mark scales down about the exact screen centre as the green fades out. The mark + "LVII" wordmark lockup is centred as one unit.
5. The mark flies to the header logo's exact position and hands off on the same frame with a small "snap". This alignment was verified by measurement; don't break it.
The user wants scene changes snappy and clean.

## Story (10 scenes, ~50s, Gen Z tone)
9:47 pm clock → sink ("remember me?") → house texting (Hinglish notifications) → chore list → "second shift… Not the vibe" → "what if coming home just meant… coming home?" → floor plan ("No 'adjust kar lo'") → chores ticked "Sorted" → one bill ("That's it, that's the post") → "Coming soon. Starting in Lucknow." with a CTA.
A `fit()` function scales each scene down to fit the frame on small or landscape screens. `.scene` uses `place-content:center`.

## Survey
Questions: profile, current living, painful chores (multi-select), room type, meals (multi-select), budget (under ₹12k / 12–18k / 18–25k / 25k+; these are placeholder bands), flat setup (women-only / men-only / mixed), move-in timing. Single-choice questions auto-advance. The waitlist form asks for name, a validated Indian WhatsApp number, optional email and a consent box.

## Mobile work already done
Side margins, the video visible on the first screen, a landscape fit, 44px tap targets, a short "Join" header label at ≤400px, and a counter that always shows. Checked at 320, 375, 390, 430, 844×390, 768, 1024 and 1440 with no sideways scrolling or scene overflow.

## Open items
- Deploy the Apps Script and set `CONFIG.endpoint`.
- Connect the repo to Vercel (preset: Other, no build command, root output).
- Venture name is still TBD. "Co-living" is a placeholder.
- Get a proper vector logo.
- Confirm or adjust the budget bands.
