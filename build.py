#!/usr/bin/env python3
"""Builds the MAFCO website from data/ and src/ into docs/ (served by GitHub Pages).

Run:  python3 build.py
Edit: data/site.json (company details), data/brands.json (brands), src/style.css (design).
"""
import json, re, shutil, html
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
SITE = json.loads((ROOT / "data/site.json").read_text())
BRANDS = json.loads((ROOT / "data/brands.json").read_text())
EXCL = [b for b in BRANDS if b["exclusive"]]
STOCK = [b for b in BRANDS if not b["exclusive"]]
COUNTRIES = sorted({b["origin"] for b in BRANDS})
e = html.escape

def words(n):
    return ["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve",
            "thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen","twenty"][n] if n <= 20 else str(n)

def roadline(cls="road"):
    svg = (ROOT / "src/assets/mafco-skyline.svg").read_text()
    path = re.search(r"<path [^>]*/>", svg).group(0)
    path = re.sub(r'stroke="[^"]*"', 'stroke="currentColor"', path)
    path = path.replace("<path ", '<path pathLength="1" ')
    dot = path.replace("<path ", '<path class="road-dot" ', 1)
    return f'<svg class="{cls}" viewBox="0 617 595.28 102" preserveAspectRatio="none" aria-hidden="true">{path}{dot}</svg>'

def gears():
    return (ROOT / "src/gears.svg").read_text()

def page(path, title, desc, body, active="", cls=""):
    depth = len(Path(path).parts) - 1
    r = "../" * depth
    canonical = SITE["url"] + "/" + (str(Path(path).parent) + "/" if Path(path).name == "index.html" and depth else ("" if path == "index.html" else path))
    def nav(href, label, key):
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{r}{href}"{cur}>{label}</a>'
    links = nav("brands/", "Brands", "brands") + nav("story/", "Our story", "story") + nav("partner/", "For suppliers", "partner")
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE['url']}/assets/img/share.png">
<link rel="icon" href="{r}favicon.ico" sizes="48x48">
<link rel="icon" href="{r}assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{r}assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="{r}assets/apple-touch-icon.png">
<link rel="preload" href="{r}assets/fonts/jost-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}style.css">
</head>
<body class="{cls}">
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <a class="logo" href="{r}" aria-label="MAFCO home"><img src="{r}assets/mafco-logo.svg" alt="MAFCO, since 1987" width="168" height="50"></a>
  <nav class="nav" aria-label="Main">
    <div class="links">{links}</div>
    <a class="btn" href="{r}contact/">Contact us</a>
  </nav>
</header>
<main id="main">
{body.replace("{r}", r)}
</main>
<footer class="foot">
  <div class="wrap foot-grid">
    <div>
      <img src="{r}assets/mafco-logo.svg" alt="MAFCO, since 1987" width="140" height="42">
      <p class="motto">Never Stop.</p>
    </div>
    <nav aria-label="Footer">
      <a href="{r}brands/">Brands</a>
      <a href="{r}story/">Our story</a>
      <a href="{r}partner/">For suppliers</a>
      <a href="{r}contact/">Contact</a>
    </nav>
    <address>
      {e(SITE['city'])}<br>
      <a href="https://wa.me/{SITE['whatsapp']}">{e(SITE['phone'])}</a><br>
      <a href="mailto:{SITE['email']}">{e(SITE['email'])}</a>
    </address>
  </div>
  <div class="wrap legal">
    <span>© {SITE['year']} MAFCO. Exclusive agents and distributors in Lebanon and Syria since 1987.</span>
    <span>All brand names and logos belong to their respective owners.</span>
  </div>
</footer>
<script src="{r}site.js" defer></script>
</body>
</html>
"""
    out = OUT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)

def tile(b, r="{r}"):
    cls = "tile" + (" dark" if b.get("dark") else "") + (" tall" if b.get("tall") else "")
    return (f'<a class="{cls}" href="{r}brands/{b["slug"]}/">'
            f'<span class="tile-logo"><img src="{r}assets/brands/{b["logo"]}" alt="{e(b["name"])}" loading="lazy"></span>'
            f'<span class="tile-meta"><b>{e(b["name"])}</b><i>{e(b["category"])}</i></span></a>')

CAPS = [
    ("One partner, two markets", "A single relationship covers Lebanon and Syria, with MAFCO people on the ground in both."),
    ("Stock held locally", "We import and hold inventory in our own warehouse, so the trade is supplied from stock, not from a catalogue."),
    ("A sales team on the road", "Our field sales team visits customers week in, week out, opening accounts and keeping shelves full."),
    ("Every channel", "Wholesalers, mechanic shops, retailers and hypermarkets. More than 1,500 customers buy from MAFCO."),
    ("Brands built in public", "From motorsport days to trade events, we put our brands in front of the drivers and mechanics who choose them."),
    ("Relationships that last", "Family-run since 1987 and now led by its second generation. We choose brands carefully and stay with them."),
]
def caps():
    return '<div class="caps">' + "".join(f"<div><h3>{e(h)}</h3><p>{e(p)}</p></div>" for h, p in CAPS) + "</div>"

def cta(h="Looking for a distributor in Lebanon or Syria?", p="Tell us about your brand and where you want to take it."):
    return f"""<section class="cta"><div class="wrap cta-in">
  <div><h2>{h}</h2><p>{p}</p></div>
  <a class="btn white" href="{{r}}partner/#enquiry">Start a conversation</a>
</div></section>"""

# ---------------------------------------------------------------- HOME
n = len(BRANDS)
home = f"""
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">Exclusive agents &amp; distributors · Since 1987</p>
    <h1>The road into <em>Lebanon &amp; Syria</em> for the world's best automotive brands.</h1>
    <p class="lede">MAFCO imports, stocks and sells leading lubricant, car care and repair brands to more than 1,500 trade customers, from mechanic shops to hypermarkets.</p>
    <p class="actions"><a class="btn" href="{{r}}partner/">Partner with us</a><a class="btn line" href="{{r}}brands/">See our brands</a></p>
  </div>
  {roadline()}
  <div class="wrap">
    <dl class="facts">
      <div><dt>1987</dt><dd>Founded in Lebanon by Jacques Homsy</dd></div>
      <div><dt>2</dt><dd>Markets served: Lebanon and Syria</dd></div>
      <div><dt>1,500+</dt><dd>Trade customers, from workshops to hypermarkets</dd></div>
      <div><dt>{n}</dt><dd>International brands from {words(len(COUNTRIES))} countries</dd></div>
    </dl>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="head">
      <h2>The brands we carry</h2>
      <p>{words(n).capitalize()} names that mechanics and drivers ask for. {words(len(EXCL)).capitalize()} of them have made MAFCO their exclusive agent.</p>
    </div>
    <div class="wall">{"".join(tile(b) for b in BRANDS)}</div>
    <p class="more"><a class="arrow" href="{{r}}brands/">All brands and what we stock</a></p>
  </div>
</section>

<section class="section grey angled">
  <div class="wrap">
    <div class="head">
      <h2>What a brand gets with MAFCO</h2>
      <p>We are the whole route to market: importer, warehouse, sales force and brand builder under one roof.</p>
    </div>
    {caps()}
  </div>
</section>

<section class="section philosophy">
  <div class="wrap">
    <blockquote class="pq">
      <p>We have a philosophy: never underestimate your customers.</p>
      <footer>Every brand we represent has gone through several cycles of testing for quality and performance before it reaches a MAFCO customer.</footer>
    </blockquote>
  </div>
</section>

<section class="story-teaser">
  <div class="wrap split">
    <div>
      <p class="eyebrow">Our story</p>
      <h2>Never stop moving.</h2>
      <p>Founded in 1987 by Jacques Homsy, MAFCO began as the exclusive distributor of quality European automotive products in Lebanon. Today it serves Lebanon and Syria, and stands as a symbol of resilience in a region too often tested.</p>
      <p><a class="arrow light" href="{{r}}story/">Read MAFCO's story</a></p>
    </div>
    <figure>{gears()}</figure>
  </div>
</section>
{cta()}
"""
page("index.html", "MAFCO | Automotive brand distribution in Lebanon & Syria since 1987",
     f"MAFCO is the exclusive agent and distributor in Lebanon and Syria for leading automotive brands including Prestone, BIZOL, Redex, Holts and Simoniz. Since 1987.",
     home, cls="home")

# ---------------------------------------------------------------- BRANDS INDEX
def row(b):
    since = f"Since {b['since']}" if b["since"] else ""
    meta = " · ".join(x for x in [b["origin"], since] if x)
    cls = "brow-logo" + (" dark" if b.get("dark") else "") + (" tall" if b.get("tall") else "")
    return f"""<a class="brow" href="{{r}}brands/{b['slug']}/">
  <span class="{cls}"><img src="{{r}}assets/brands/{b['logo']}" alt="" loading="lazy"></span>
  <span class="brow-text"><b>{e(b['name'])}</b><span>{e(b['summary'])}</span></span>
  <span class="brow-meta"><i>{e(b['category'])}</i><span>{e(meta)}</span></span>
</a>"""
brands_idx = f"""
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">Our brands</p>
    <h1>{words(n).capitalize()} brands. One distributor.</h1>
    <p class="lede">Lubricants, coolants, additives, car care, tyre repair and engine parts from {", ".join(COUNTRIES[:-1])} and {COUNTRIES[-1]}, supplied to the trade across Lebanon and Syria.</p>
  </div>
</section>
<section class="section tight">
  <div class="wrap">
    <div class="group-head"><h2>Exclusive agencies</h2><p>MAFCO is the exclusive agent and distributor for these brands in Lebanon and Syria.</p></div>
    <div class="brows">{"".join(row(b) for b in EXCL)}</div>
    <div class="group-head"><h2>Also in our range</h2><p>Brands we stock and supply alongside our exclusive agencies.</p></div>
    <div class="brows">{"".join(row(b) for b in STOCK)}</div>
  </div>
</section>
{cta("Trade customer?", "Ask us for availability, pricing and the full range of any brand.").replace("partner/#enquiry", "contact/").replace("Start a conversation", "Contact sales")}
"""
page("brands/index.html", "Our brands | MAFCO",
     "The automotive brands MAFCO distributes in Lebanon and Syria: " + ", ".join(b["name"] for b in BRANDS) + ".",
     brands_idx, active="brands")

# ---------------------------------------------------------------- BRAND PAGES
for i, b in enumerate(BRANDS):
    prev, nxt = BRANDS[i - 1], BRANDS[(i + 1) % n]
    status = ("Exclusive agent · Lebanon &amp; Syria" if b["exclusive"] else "Stocked by MAFCO")
    since = f"<div><dt>Since</dt><dd>{e(b['since'])}</dd></div>" if b["since"] else ""
    logo_cls = "blogo" + (" dark" if b.get("dark") else "") + (" tall" if b.get("tall") else "")
    body = f"""
<section class="pagehead brandhead">
  <div class="wrap">
    <p class="crumbs"><a href="{{r}}brands/">Brands</a> <span>/</span> {e(b['name'])}</p>
    <div class="brand-top">
      <div class="{logo_cls}"><img src="{{r}}assets/brands/{b['logo']}" alt="{e(b['name'])} logo"></div>
      <div>
        <p class="status{' ex' if b['exclusive'] else ''}">{status}</p>
        <h1>{e(b['name'])}</h1>
        <p class="lede">{e(b['description'])}</p>
        <dl class="meta">
          <div><dt>Category</dt><dd>{e(b['category'])}</dd></div>
          <div><dt>Origin</dt><dd>{e(b['origin'])}</dd></div>
          {since}
        </dl>
      </div>
    </div>
  </div>
</section>
<section class="section tight">
  <div class="wrap two">
    <div>
      <h2>Product ranges</h2>
      <ul class="ranges">{"".join(f"<li>{e(x)}</li>" for x in b['ranges'])}</ul>
    </div>
    <div>
      <h2>About the brand</h2>
      <ul class="factlist">{"".join(f"<li>{e(x)}</li>" for x in b['facts'])}</ul>
      <p class="src">Brand information from <a href="{b['url']}" rel="noopener">{e(b['site'])}</a></p>
    </div>
  </div>
</section>
<section class="section grey enquire">
  <div class="wrap enquire-in">
    <div>
      <h2>Stocking {e(b['name'])} in Lebanon or Syria?</h2>
      <p>Talk to MAFCO for availability, the full range and trade pricing.</p>
    </div>
    <p class="actions"><a class="btn" href="https://wa.me/{SITE['whatsapp']}">WhatsApp us</a><a class="btn line" href="mailto:{SITE['email']}?subject={e(b['name'])}%20enquiry">Email sales</a></p>
  </div>
</section>
<nav class="pager wrap" aria-label="More brands">
  <a href="{{r}}brands/{prev['slug']}/"><span>Previous</span><b>{e(prev['name'])}</b></a>
  <a href="{{r}}brands/{nxt['slug']}/"><span>Next</span><b>{e(nxt['name'])}</b></a>
</nav>
"""
    page(f"brands/{b['slug']}/index.html", f"{b['name']} in Lebanon & Syria | MAFCO",
         f"{b['name']}: {b['summary']} {'Exclusively distributed' if b['exclusive'] else 'Supplied'} in Lebanon and Syria by MAFCO.",
         body, active="brands")

# ---------------------------------------------------------------- STORY
story = f"""
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">Our story</p>
    <h1>Never stop moving.</h1>
    <p class="lede">MAFCO is a story of purpose, perseverance, and people. Our motto, “Never Stop,” isn't just a slogan. It's a promise we've kept for generations.</p>
  </div>
</section>
<section class="section tight">
  <div class="wrap">
    <figure class="wide">{gears()}</figure>
    <ol class="timeline">
      <li><b>1987</b><div><h2>A beginning in Dora</h2><p>Founded by Jacques Homsy, MAFCO began as the exclusive distributor of quality European automotive products in Lebanon. For over 25 years, from its base in Dora, Jacques built strong relationships with wholesalers and laid the foundation of a business that valued trust, reliability, and family.</p></div></li>
      <li><b>2002</b><div><h2>The next generation</h2><p>Jacques brought his young son Marc into the business: weekends, summers, holidays. What started as father-son bonding became an informal apprenticeship. Jacques was preparing Marc not just to understand the trade, but to carry its torch forward when the time came.</p></div></li>
      <li><b>Today</b><div><h2>Lebanon and Syria</h2><p>MAFCO stands as the exclusive distributor of automotive products across Lebanon and Syria, and a symbol of resilience in a region too often tested. We continue to grow, not for the sake of scale, but to create opportunities for talented, driven individuals who share our spirit.</p></div></li>
    </ol>
    <p class="signoff">Because at MAFCO, we never stop moving.</p>
  </div>
</section>
{cta()}
"""
page("story/index.html", "Our story | MAFCO", "Founded in 1987 by Jacques Homsy, MAFCO is a family business distributing automotive brands across Lebanon and Syria.", story, active="story")

# ---------------------------------------------------------------- PARTNER
strip = "".join(f'<span class="{"dark" if b.get("dark") else ""}{" tall" if b.get("tall") else ""}"><img src="{{r}}assets/brands/{b["logo"]}" alt="{e(b["name"])}" loading="lazy"></span>' for b in BRANDS)
partner = f"""
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">For suppliers</p>
    <h1>Bring your brand to <em>Lebanon &amp; Syria</em>.</h1>
    <p class="lede">Since 1987, international manufacturers have relied on MAFCO to import, stock, sell and build their brands in two demanding markets. Here is what we bring.</p>
  </div>
</section>
<section class="section tight">
  <div class="wrap">
    {caps()}
  </div>
</section>
<section class="section grey angled">
  <div class="wrap">
    <div class="head">
      <h2>In good company</h2>
      <p>{words(n).capitalize()} brands from {", ".join(COUNTRIES[:-1])} and {COUNTRIES[-1]} reach the trade through MAFCO. {words(len(EXCL)).capitalize()} of them on an exclusive basis.</p>
    </div>
    <div class="strip">{strip}</div>
    <dl class="facts on-grey">
      <div><dt>1987</dt><dd>Distributing international brands ever since</dd></div>
      <div><dt>1,500+</dt><dd>Active trade customers</dd></div>
      <div><dt>{len(EXCL)}</dt><dd>Exclusive agencies</dd></div>
      <div><dt>2</dt><dd>Markets, one partner</dd></div>
    </dl>
  </div>
</section>
<section class="section" id="enquiry">
  <div class="wrap two">
    <div>
      <h2>Start a conversation</h2>
      <p>Tell us what you make and what you are looking for in the region. It helps if you include:</p>
      <ul class="ranges">
        <li>Your brand and product categories</li>
        <li>Where you are sold today in the Middle East</li>
        <li>Whether you are looking for an exclusive agent</li>
      </ul>
      <p>Prefer to write directly? <a href="mailto:{SITE['email']}">{SITE['email']}</a> or WhatsApp <a href="https://wa.me/{SITE['whatsapp']}">{SITE['phone']}</a>.</p>
    </div>
    <form class="form" id="enquiry-form" data-to="{SITE['email']}">
      <label for="f-name">Your name<input id="f-name" name="name" required autocomplete="name"></label>
      <label for="f-company">Company or brand<input id="f-company" name="company" required autocomplete="organization"></label>
      <label for="f-msg">What are you looking for?<textarea id="f-msg" name="message" rows="5" required></textarea></label>
      <button class="btn" type="submit">Write the email</button>
      <p class="hint" id="f-hint">This opens your email app with the message ready to send to MAFCO.</p>
    </form>
  </div>
</section>
"""
page("partner/index.html", "For suppliers | MAFCO, your distributor in Lebanon & Syria",
     "Looking for a distributor in Lebanon or Syria? MAFCO imports, stocks, sells and builds international automotive brands. Own warehouse, field sales team, 1,500+ trade customers.",
     partner, active="partner")

# ---------------------------------------------------------------- CONTACT
contact = f"""
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">Contact</p>
    <h1>Talk to MAFCO.</h1>
    <p class="lede">Trade customer, supplier or just looking for one of our brands: we are easy to reach.</p>
  </div>
</section>
<section class="section tight">
  <div class="wrap two">
    <dl class="contact-list">
      <div><dt>Mobile / WhatsApp</dt><dd><a href="https://wa.me/{SITE['whatsapp']}">{SITE['phone']}</a></dd></div>
      <div><dt>Email</dt><dd><a href="mailto:{SITE['email']}">{SITE['email']}</a></dd></div>
      <div><dt>Location</dt><dd>{e(SITE['location'])}</dd></div>
      <div><dt>Suppliers</dt><dd><a class="arrow" href="{{r}}partner/">Partner with MAFCO</a></dd></div>
    </dl>
    <iframe class="map" title="Map showing MAFCO's location in Lebanon" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://www.google.com/maps?q={SITE['map_query']}&z=14&output=embed"></iframe>
  </div>
</section>
"""
page("contact/index.html", "Contact | MAFCO", "Contact MAFCO in Lebanon: WhatsApp +961 71 30 88 34 or NeverStop@mafcotrading.com.", contact, active="contact")

page("404.html", "Page not found | MAFCO", "This page does not exist.",
     f"""<section class="pagehead"><div class="wrap"><p class="eyebrow">404</p><h1>Wrong turn.</h1><p class="lede">That page doesn't exist. The road continues from the home page.</p><p class="actions"><a class="btn" href="/">Back to home</a></p></div></section>""")

# ---------------------------------------------------------------- STATIC FILES
shutil.copytree(ROOT / "src/assets", OUT / "assets", dirs_exist_ok=True)
for f in ("style.css", "site.js", "favicon.ico"):
    shutil.copy(ROOT / "src" / f, OUT / f)
# Set "use_custom_domain": true in data/site.json once the domain's DNS points to GitHub Pages.
if SITE.get("use_custom_domain"):
    (OUT / "CNAME").write_text(SITE["domain"] + "\n")
elif (OUT / "CNAME").exists():
    (OUT / "CNAME").unlink()
(OUT / ".nojekyll").write_text("")
urls = ["", "brands/", "story/", "partner/", "contact/"] + [f"brands/{b['slug']}/" for b in BRANDS]
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{SITE['url']}/{u}</loc></url>\n" for u in urls) + "</urlset>\n")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")
print(f"Built {len(urls) + 1} pages into {OUT}")
