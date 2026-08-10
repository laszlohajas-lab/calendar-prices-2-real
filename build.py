#!/usr/bin/env python3
"""Regenerate the two Useberry test variants from the single source of truth.

Source of truth: index.html (the full build WITH the behaviour toggle).
Run `python3 build.py` after any design change; it writes:
  useberry-deploy/version-a.html  -> Static  (V1, behaviour='static')
  useberry-deploy/version-b.html  -> Dynamic (V2, behaviour='separate')
  useberry-deploy/index.html      -> private reference landing
The variants are byte-identical except the locked behaviour, and both keep
the title "Prices Calendar" so testers can't tell them apart.
"""
import os, sys

SRC = "index.html"
OUT = "useberry-deploy"

def main():
    src = open(SRC, encoding="utf-8").read()
    # strip the floating debug toggle (from its div to the footer that follows)
    try:
        start = src.index('  <div class="mode-switch"')
        end = src.index('  <footer class="hint">')
    except ValueError:
        sys.exit("ERROR: couldn't locate the mode-switch toggle block in index.html")
    base = src[:start] + '  <!-- behaviour locked for user test; toggle removed -->\n\n' + src[end:]

    if "behavior: 'static'," not in base:
        sys.exit("ERROR: couldn't find the behaviour default in index.html")

    # Useberry "Live Website" tracking snippet — injected into the test builds only,
    # not into the master source (index.html stays product-clean).
    USEBERRY = '<script type="text/javascript" src="https://api.useberry.com/integrations/liveUrl/scripts/useberryScript.js"></script>'
    def inject(html):
        if "useberryScript.js" in html:
            return html
        if "</body>" not in html:
            sys.exit("ERROR: no </body> tag to inject the Useberry snippet before")
        return html.replace("</body>", "  " + USEBERRY + "\n</body>", 1)

    os.makedirs(OUT, exist_ok=True)
    # Variant A: Static (default already 'static')
    open(os.path.join(OUT, "version-a.html"), "w", encoding="utf-8").write(inject(base))
    # Variant B: Dynamic ('separate')
    open(os.path.join(OUT, "version-b.html"), "w", encoding="utf-8").write(
        inject(base.replace("behavior: 'static',", "behavior: 'separate',", 1)))
    # private reference landing
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Prices Calendar &mdash; test builds</title>'
        '<style>body{font-family:system-ui,sans-serif;max-width:640px;margin:60px auto;padding:0 20px;color:#00223e}a{color:#0a66c2}</style>'
        '</head><body><h1>Prices Calendar &mdash; test builds</h1>'
        '<p>Private index for your reference (testers get the direct links).</p><ul>'
        '<li><a href="version-a.html">version-a.html</a> &mdash; Variant A (Static / V1)</li>'
        '<li><a href="version-b.html">version-b.html</a> &mdash; Variant B (Dynamic / V2)</li>'
        '</ul></body></html>')
    print("Built useberry-deploy/{version-a.html, version-b.html, index.html} from", SRC)

if __name__ == "__main__":
    main()
