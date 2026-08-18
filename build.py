#!/usr/bin/env python3
"""Regenerate the Useberry test variants from the single sources of truth.

Sources of truth (edit design changes HERE, never in useberry-deploy/):
  index.html         -> desktop build, WITH the behaviour toggle
  index-mobile.html  -> mobile build,  WITH the behaviour toggle

Run `python3 build.py` after any design change; it writes into useberry-deploy/:
  version-a.html  desktop  Static  (behaviour='static')
  version-b.html  desktop  Dynamic (behaviour='separate')
  mobile-a.html   mobile   Static  (behaviour='static')
  mobile-b.html   mobile   Dynamic (behaviour='separate')
  index.html      private reference landing

Within each platform the two variants are byte-identical except the locked
behaviour, and both keep the title "Prices Calendar" so testers can't tell
them apart. The Useberry tracking snippet is injected into the test builds
only, never into the sources.

NOTE: useberry-deploy/report.html is NOT generated here — it is the findings
write-up, placed by hand and deliberately left out of the landing page so
participants can't stumble onto the results mid-study. This script only ever
writes the five files listed above, so the report survives a rebuild.
"""
import os, sys

DESKTOP_SRC = "index.html"
MOBILE_SRC = "index-mobile.html"
OUT = "useberry-deploy"

USEBERRY = ('<script type="text/javascript" '
            'src="https://api.useberry.com/integrations/liveUrl/scripts/useberryScript.js"></script>')


def read(path):
    if not os.path.exists(path):
        sys.exit("ERROR: missing source file %s" % path)
    return open(path, encoding="utf-8").read()


def strip_desktop_toggle(src):
    """Desktop: remove the floating toggle block (div .mode-switch → footer.hint)."""
    try:
        start = src.index('  <div class="mode-switch"')
        end = src.index('  <footer class="hint">')
    except ValueError:
        sys.exit("ERROR: couldn't locate the mode-switch toggle block in " + DESKTOP_SRC)
    return src[:start] + '  <!-- behaviour locked for user test; toggle removed -->\n\n' + src[end:]


def strip_mobile_toggle(src):
    """Mobile: remove everything between the explicit marker comments."""
    s, e = '<!--MODE_SWITCH_START-->', '<!--MODE_SWITCH_END-->'
    if s not in src or e not in src:
        sys.exit("ERROR: couldn't locate the MODE_SWITCH markers in " + MOBILE_SRC)
    start = src.index(s)
    end = src.index(e) + len(e)
    return src[:start] + '<!-- behaviour locked for user test; toggle removed -->' + src[end:]


def inject_snippet(html):
    """Useberry Live-Website tracking snippet, last item in the <body>."""
    if "useberryScript.js" in html:
        return html
    if "</body>" not in html:
        sys.exit("ERROR: no </body> tag to inject the Useberry snippet before")
    return html.replace("</body>", "  " + USEBERRY + "\n</body>", 1)


def make_variants(base, label):
    """Return (static_html, dynamic_html) with the behaviour locked in each."""
    if "behavior: 'static'," not in base:
        sys.exit("ERROR: couldn't find the behaviour default in the %s source" % label)
    static = base
    dynamic = base.replace("behavior: 'static',", "behavior: 'separate',", 1)
    if dynamic == base:
        sys.exit("ERROR: failed to switch the behaviour for the %s dynamic build" % label)
    return inject_snippet(static), inject_snippet(dynamic)


LANDING = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>Prices Calendar &mdash; test builds</title>'
    '<style>body{font-family:system-ui,sans-serif;max-width:640px;margin:60px auto;padding:0 20px;'
    'color:#00223e}a{color:#0a66c2}h2{font-size:16px;margin-top:28px}</style>'
    '</head><body><h1>Prices Calendar &mdash; test builds</h1>'
    '<p>Private index for your reference (testers get the direct links).</p>'
    '<h2>Desktop</h2><ul>'
    '<li><a href="version-a.html">version-a.html</a> &mdash; Variant A (Static)</li>'
    '<li><a href="version-b.html">version-b.html</a> &mdash; Variant B (Dynamic)</li>'
    '</ul><h2>Mobile</h2><ul>'
    '<li><a href="mobile-a.html">mobile-a.html</a> &mdash; Variant A (Static)</li>'
    '<li><a href="mobile-b.html">mobile-b.html</a> &mdash; Variant B (Dynamic)</li>'
    '</ul></body></html>'
)


def main():
    os.makedirs(OUT, exist_ok=True)

    desktop_a, desktop_b = make_variants(strip_desktop_toggle(read(DESKTOP_SRC)), "desktop")
    mobile_a, mobile_b = make_variants(strip_mobile_toggle(read(MOBILE_SRC)), "mobile")

    files = {
        "version-a.html": desktop_a,
        "version-b.html": desktop_b,
        "mobile-a.html": mobile_a,
        "mobile-b.html": mobile_b,
        "index.html": LANDING,
    }
    for name, content in files.items():
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(content)

    print("Built %s/: %s" % (OUT, ", ".join(sorted(files))))


if __name__ == "__main__":
    main()
