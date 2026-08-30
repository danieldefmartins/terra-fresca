#!/usr/bin/env python3
"""Build the produce portal.

  produce/data.py  ->  produce/<slug>/index.html
                       produce/index.html

Reuses the blog's shell and stylesheet so the whole site outside the animated
home page is one consistent set of pages. Run buildblog.py after this so the
sitemap picks the produce URLs up.
"""
import html, pathlib, sys

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT / "produce"))
import data as D  # noqa: E402

SITE = "https://terrafrescatrading.com"
WA_US = ("https://wa.me/19543523599?text=Hi%20Terra%20Fresca%20%E2%80%94%20I%27d%20like%20to"
         "%20talk%20about%20sourcing%20fruit%20from%20Brazil.")


def calendar(peak, available):
    """Twelve cells: solid for the export window, tinted where fruit can be had."""
    cells = ""
    for m in range(1, 13):
        cls = "pk" if m in peak else ("av" if m in available else "")
        cells += (f"<span class='{cls}' title='{D.MONTH_NAMES[m-1]}'>"
                  f"<i>{D.MONTHS[m-1]}</i></span>")
    return (f"<div class='cal'>{cells}</div>"
            "<p class='callegend'><b></b> Export window <b class='b2'></b> Also available</p>")


def shell(title, desc, canonical, body):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#021F36">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Terra Fresca Trading">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/blog/blog.css">
</head>
<body>
<header class="bhead">
  <a class="blogo" href="/"><b>TERRA FRESCA</b><i>Global Produce Trading</i></a>
  <nav><a href="/">Home</a><a href="/produce/">Produce</a><a href="/blog/">Blog</a><a href="/#cta">Contact</a></nav>
</header>
{body}
<footer class="bfoot">
  <div class="fgrid">
    <div class="fcol wide">
      <p class="tag">From Brazilian soil.<br>To tables worldwide.</p>
      <p class="sm">Over fifteen years trading Brazilian produce, with more than thirty partner
      farms and retail across Minas Gerais and S&#227;o Paulo.</p>
    </div>
    <div class="fcol">
      <h4>Produce</h4>
      {"".join(f'<a href="/produce/{p["slug"]}/">{html.escape(p["name"])}</a>' for p in D.PRODUCTS[:6])}
      <a href="/produce/">All produce &#8594;</a>
    </div>
    <div class="fcol">
      <h4>Company</h4>
      <a href="/">Home</a><a href="/#services">Services</a><a href="/blog/">Blog</a>
      <a href="/#voices">Buyers</a><a href="/#cta">Contact</a>
    </div>
    <div class="fcol">
      <h4>Contact</h4>
      <a href="mailto:trade@terrafrescatrading.com">trade@terrafrescatrading.com</a>
      <span class="off">Brazil</span>
      <span>Av. Pres. Ant&#244;nio Carlos, 4048<br>Pampulha, Belo Horizonte &#8212; MG<br>31270-000</span>
      <span class="off">United States</span>
      <span>433 Plaza Real, Suite 275<br>Boca Raton, FL 33432</span>
      <a href="{WA_US}" target="_blank" rel="noopener">WhatsApp &#183; +1 954 352 3599</a>
    </div>
  </div>
  <div class="fbot"><span>&#169; 2026 Terra Fresca Trading</span><span>Global produce trading &#183; Brazil</span></div>
</footer>
<button class="to-top" id="toTop" type="button" aria-label="Back to top"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M6 11l6-6 6 6"/></svg></button>
<script>
(function(){{var b=document.getElementById("toTop");if(!b)return;
b.addEventListener("click",function(){{window.scrollTo({{top:0,behavior:"smooth"}})}});
addEventListener("scroll",function(){{b.classList.toggle("on",scrollY>innerHeight*0.9)}},{{passive:true}});}})();
</script>
</body>
</html>
"""


def product_page(p):
    url = f"{SITE}/produce/{p['slug']}/"
    organic = ("<p>" + html.escape(D.ORGANIC_NOTE) + "</p>"
               + ("<p class='tbc'>Organic availability on this line is confirmed per programme &#8212; "
                  "ask us what is certified for the season you are buying.</p>"
                  if p.get("organic") == "TBC" else
                  f"<p>{html.escape(p.get('organic',''))}</p>"))

    grapes = ""
    if p["slug"] == "seedless-grape":
        grapes = ("<h2>The three colours</h2><div class='colours'>" + "".join(
            f"<div class='colour'><img src='/assets/{img}.webp' alt='Crate of {c.lower()} seedless grapes' loading='lazy'>"
            f"<h3>{c}</h3><p class='sm'>{v}</p></div>"
            for c, img, v in D.GRAPE_COLOURS) + "</div>")

    body = f"""<main class='prod'>
<div class='phero'>
  <div>
    <p class='kick'>{html.escape(p['tag'])} &#183; Brazil</p>
    <h1>{html.escape(p['name'])}</h1>
    <p class='latin'>{html.escape(p['latin'])}</p>
    <p class='lede'>{html.escape(p['blurb'])}</p>
    <div class='bcta'>
      <a class='bbtn solid' href='{WA_US}' target='_blank' rel='noopener'>Ask about {html.escape(p['name'].lower())}</a>
      <a class='bbtn' href='mailto:trade@terrafrescatrading.com'>Request a quote</a>
    </div>
  </div>
  <img class='pcrate' src='/assets/{p['crate']}.webp' alt='Crate of Brazilian {html.escape(p['name'].lower())}'>
</div>

<section class='pblock'>
  <h2>Availability through the year</h2>
  {calendar(p['peak'], p['available'])}
  {f"<p>{html.escape(p['second_window'])}</p>" if p.get('second_window') else ""}
</section>

<div class='pgrid'>
  <section class='pblock'>
    <h2>Varieties</h2>
    <ul class='pills'>{"".join(f"<li>{html.escape(v)}</li>" for v in p['varieties'])}</ul>
  </section>
  <section class='pblock'>
    <h2>Where it grows</h2>
    <ul class='pills alt'>{"".join(f"<li>{html.escape(s)}</li>" for s in p['states'])}</ul>
    <p class='sm'>{html.escape(D.REACH_NOTE)}</p>
  </section>
</div>

<section class='pblock'>
  <h2>What matters on this line</h2>
  <p>{html.escape(p['notes'])}</p>
  {f"<p><a href='{p['link']}'>Read more &#8594;</a></p>" if p.get('link') else ""}
</section>

{grapes}

<section class='pblock'>
  <h2>Organic</h2>
  {organic}
</section>

<section class='pblock volume'>
  <h2>Volume and packing</h2>
  <p>Volume is agreed per programme rather than quoted from a list. Tell us the weekly quantity,
  the calibre and the format you need, and the window you need it in, and we will tell you what
  Brazil can actually deliver against it.</p>
  <div class='bcta'>
    <a class='bbtn solid' href='{WA_US}' target='_blank' rel='noopener'>Tell us your programme</a>
  </div>
</section>

<nav class='pnext'><h2>Other lines</h2><div class='cards'>{"".join(
  f"<a class='card' href='/produce/{o['slug']}/'><span class='kick'>{html.escape(o['tag'])}</span>"
  f"<h2>{html.escape(o['name'])}</h2><p>{html.escape(o['blurb'])}</p></a>"
  for o in D.PRODUCTS if o['slug'] != p['slug'])}</div></nav>
</main>"""

    desc = (f"{p['name']} from Brazil — {', '.join(p['varieties'][:3])}. "
            f"Grown in {', '.join(s.split(' (')[0] for s in p['states'][:3])}. "
            f"{p['blurb']}")
    d = ROOT / "produce" / p["slug"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(
        shell(f"{p['name']} from Brazil — varieties, season and sourcing | Terra Fresca",
              desc[:300], url, body), encoding="utf-8")


def index_page():
    cards = "".join(
        f"<a class='pcard' href='/produce/{p['slug']}/'>"
        f"<img src='/assets/{p['crate']}.webp' alt='Crate of Brazilian {html.escape(p['name'].lower())}' loading='lazy'>"
        f"<span class='kick'>{html.escape(p['tag'])}</span>"
        f"<h2>{html.escape(p['name'])}</h2><p>{html.escape(p['blurb'])}</p></a>"
        for p in D.PRODUCTS)
    body = ("<div class='masthead'><div class='mwrap'>"
            "<p class='kick'>Terra Fresca &#183; Produce</p>"
            "<h1>What Brazil can send you</h1>"
            "<p class='lede'>Every line we trade, with the varieties, the growing states and the "
            "months each one is actually available. We represent farms across Brazil rather than a "
            "fixed grower list, so the supply base is built around your programme.</p>"
            "</div></div>"
            f"<main class='index'><div class='pcards'>{cards}</div>"
            "<section class='pblock volume'><h2>Not seeing a line?</h2>"
            "<p>Brazil grows a great deal more than this. If you need something that is not listed, "
            "tell us the specification and the window and we will find out whether it can be done.</p>"
            f"<div class='bcta'><a class='bbtn solid' href='{WA_US}' target='_blank' rel='noopener'>Ask us</a></div>"
            "</section></main>")
    (ROOT / "produce" / "index.html").write_text(
        shell("Brazilian fresh produce — varieties, seasons and availability | Terra Fresca",
              "Every fresh produce line Terra Fresca trades out of Brazil: mango, seedless grape, "
              "melon, papaya, lime, banana, pineapple, watermelon, avocado, ginger, sweet potato "
              "and passion fruit — with varieties, growing states and month-by-month availability.",
              f"{SITE}/produce/", body), encoding="utf-8")


def main():
    for p in D.PRODUCTS:
        product_page(p)
    index_page()
    print(f"produce: {len(D.PRODUCTS)} product pages + index")


if __name__ == "__main__":
    main()
