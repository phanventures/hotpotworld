#!/usr/bin/env python3
"""Bundle the five-page static site into ONE self-contained HTML for phone preview.

The published Artifact runs under a CSP that blocks every external host, and it
is a single file, so this script inlines the stylesheet and base64s every image.
The five pages become five sections switched by the existing nav.

Run from the Website/ root:  python3 source/build_preview.py
"""
import base64, io, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

PAGES = [
    ("home",  "index.html"),
    ("how",   "how-it-works.html"),
    ("menu",  "menu.html"),
    ("about", "about.html"),
    ("visit", "contact.html"),
]
PAGE_OF_FILE = {f: k for k, f in PAGES}

# Preview-only downscale. The real site keeps its full size assets; this exists
# purely to keep the single file small enough to open over cell service.
WIDTHS = {"hero-spread": 1200, "plates": 780, "dish": 620, "room": 620}


def target_width(name):
    for key, w in WIDTHS.items():
        if name.startswith(key):
            return w
    return 700


_cache = {}


def data_uri(path):
    """Re-encode an asset as a compact base64 data URI."""
    if path in _cache:
        return _cache[path]
    disk = path.lstrip("./")
    if not os.path.exists(disk):
        raise SystemExit("missing asset: " + disk)
    name = os.path.basename(disk).split(".")[0]
    im = Image.open(disk)

    if disk.endswith(".png"):                       # logos keep transparency
        im = im.convert("RGBA")
        im.thumbnail((320, 320), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "PNG", optimize=True)
        uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    else:
        im = im.convert("RGB")
        w = target_width(name)
        if im.width > w:
            im.thumbnail((w, w * 4), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=72, method=6)
        uri = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()

    print(f"  {os.path.basename(disk):26s} {len(uri)//1024:5d} KB")
    _cache[path] = uri
    return uri


def inline_images(html):
    # srcset would double the payload for no benefit in a preview
    html = re.sub(r'\s+srcset="[^"]*"', "", html)
    html = re.sub(r'\s+sizes="[^"]*"', "", html)
    html = re.sub(r'src="(assets/img/[^"]+)"',
                  lambda m: 'src="' + data_uri(m.group(1)) + '"', html)
    # gallery lightbox links point at @2x files that are not bundled
    html = re.sub(r'<a href="assets/img/[^"]+">(.*?)</a>', r"\1", html, flags=re.S)
    return html


def grab(html, tag, cls=None):
    if cls:
        pat = r'<%s class="%s".*?>(.*?)</%s>' % (tag, cls, tag)
    else:
        pat = r"<%s.*?>(.*?)</%s>" % (tag, tag)
    m = re.search(pat, html, re.S)
    return m.group(1) if m else ""


print("inlining assets")
sources = {f: open(f).read() for _, f in PAGES}

# header and footer are identical across pages, take them once
header = grab(sources["index.html"], "header")
footer = grab(sources["index.html"], "footer")

# nav links become in-page section switches
def rewrite_nav(html):
    for f, key in PAGE_OF_FILE.items():
        html = html.replace('href="%s"' % f, 'href="#%s" data-goto="%s"' % (key, key))
    return html

header = rewrite_nav(header)
footer = rewrite_nav(footer)

sections = []
for key, f in PAGES:
    main = grab(sources[f], "main")
    main = rewrite_nav(main)
    sections.append(
        '<section class="page" id="%s"%s>%s</section>'
        % (key, "" if key == "home" else ' hidden', main)
    )

css = open("assets/css/style.css").read()

body = header + "\n" + "\n".join(sections) + "\n" + footer
body = inline_images(body)

# The YouTube facade cannot load an iframe under the Artifact CSP, so in the
# preview the play button opens YouTube in a new tab instead.
body = body.replace(
    '<button class="video" data-video-id="BQ6H78DR1zQ"',
    '<a class="video" href="https://www.youtube.com/watch?v=BQ6H78DR1zQ" '
    'target="_blank" rel="noopener" data-yt="1"'
).replace("</button>", "</a>", 1)

EXTRA = """
/* ---- preview shell -------------------------------------------------------
   This is a faithful preview of a live restaurant site that has one committed
   look, so the page pins its own light ground rather than following the
   viewer's theme. Inverting it would misrepresent what ships.            */
:root, :root[data-theme="dark"], :root[data-theme="light"] {
  color-scheme: light;
}
body { background: #fff; color: var(--ink); }

/* Static, not sticky: the site has its own sticky header pinned to top:0, and
   two sticky bars at the same offset overlap and hide the real one. */
.preview-bar {
  position: static; z-index: 200;
  display: flex; flex-wrap: wrap; align-items: center; gap: .5rem 1rem;
  padding: .7rem clamp(1rem, 4vw, 2rem);
  background: var(--ink); color: #fff;
  font-size: .82rem; letter-spacing: .01em;
}
.preview-bar b { color: #fff; font-weight: 700; }
.preview-bar span { color: rgba(255,255,255,.62); }
.preview-bar .jump { margin-left: auto; display: flex; flex-wrap: wrap; gap: .4rem; }
.preview-bar .jump button {
  font: inherit; font-weight: 600;
  padding: .3rem .8rem; border-radius: 999px; cursor: pointer;
  background: rgba(255,255,255,.1); color: #fff;
  border: 1px solid rgba(255,255,255,.22);
}
.preview-bar .jump button:hover { background: rgba(255,255,255,.2); }
.preview-bar .jump button[aria-pressed="true"] { background: var(--brand); border-color: var(--brand); }
.preview-bar .jump button:focus-visible,
.nav a:focus-visible, .btn:focus-visible { outline: 3px solid #fff; outline-offset: 2px; }

.page[hidden] { display: none; }
"""

BAR = """
<div class="preview-bar">
  <b>Hot Pot World Rotary</b>
  <span>preview build &middot; tap through all five pages</span>
  <div class="jump">
    <button type="button" data-goto="home" aria-pressed="true">Home</button>
    <button type="button" data-goto="how" aria-pressed="false">How It Works</button>
    <button type="button" data-goto="menu" aria-pressed="false">Menu</button>
    <button type="button" data-goto="about" aria-pressed="false">Our Story</button>
    <button type="button" data-goto="visit" aria-pressed="false">Visit Us</button>
  </div>
</div>
"""

JS = """
<script>
(function () {
  'use strict';
  var pages = ['home','how','menu','about','visit'];

  function show(key) {
    if (pages.indexOf(key) < 0) return;
    pages.forEach(function (p) {
      document.getElementById(p).hidden = (p !== key);
    });
    document.querySelectorAll('.preview-bar [data-goto]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.goto === key));
    });
    document.querySelectorAll('.nav a[data-goto]').forEach(function (a) {
      if (a.dataset.goto === key) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
    // Deferred: when the page is entered via #hash the browser scrolls to the
    // section itself, which lands the viewer below the header. Undo that after
    // the browser has done it, not before.
    requestAnimationFrame(function () { window.scrollTo(0, 0); });
  }

  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-goto]');
    if (!t) return;
    e.preventDefault();
    show(t.dataset.goto);
    var nav = document.querySelector('.nav'), tog = document.querySelector('.nav-toggle');
    if (nav && tog) { nav.setAttribute('data-open','false'); tog.setAttribute('aria-expanded','false'); }
  });

  // deep link support: #menu opens the menu page directly
  if (location.hash) show(location.hash.slice(1));
  window.addEventListener('hashchange', function () { show(location.hash.slice(1)); });

  var toggle = document.querySelector('.nav-toggle'), nav = document.querySelector('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.setAttribute('data-open', String(!open));
    });
  }
})();
</script>
"""

out = ('<title>Hot Pot World Rotary &middot; site preview</title>\n'
       "<style>\n" + css + EXTRA + "\n</style>\n" + BAR + body + JS)

open("source/preview.html", "w").write(out)
print("\nwrote source/preview.html  %.2f MB" % (len(out) / 1024 / 1024))
