# Prices Calendar — prototype & user-test builds

Self-contained HTML/CSS/JS flight-price calendar prototype used for Useberry A/B testing
of two calendar behaviours.

## Files
- `index.html` — **source of truth** (full build WITH the behaviour toggle). Edit design changes here.
- `v4.html`, `index_backup_v123.html`, `prices-calendar.html` — earlier versions / backups (not deployed).
- `build.py` — regenerates the two test variants from `index.html`.
- `useberry-deploy/` — the **only** folder Netlify publishes:
  - `version-a.html` — Variant A: **Static** (green = fixed overall estimate)
  - `version-b.html` — Variant B: **Dynamic** (green follows the field you're editing)
  - `index.html` — private reference landing
- `netlify.toml` — tells Netlify to publish `useberry-deploy/`.

## Workflow after a Figma design change
1. Apply the change once in `index.html`.
2. Run `python3 build.py` to regenerate both variants (they stay identical except the locked behaviour, same title — unbiased).
3. `git add -A && git commit -m "..." && git push`
4. Netlify auto-deploys. Live links (unchanged):
   - Static:  https://calendar-upgrade.netlify.app/version-a.html
   - Dynamic: https://calendar-upgrade.netlify.app/version-b.html

Never hand-edit the files in `useberry-deploy/` — they are generated.
