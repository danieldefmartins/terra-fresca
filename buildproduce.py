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
  <nav><a href="/">Home</a><a href="/produce/">Produce</a><a href="/services/">Services</a><a href="/about/">About</a><a href="/blog/">Blog</a><a href="/contact/">Contact</a></nav>
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
      <a href="/">Home</a><a href="/services/">Services</a><a href="/about/">About</a>
      <a href="/blog/">Blog</a><a href="/contact/">Contact</a>
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

    variants = ""
    if p.get("variants"):
        variants = ("<section class='pblock'><h2>Types we trade</h2>"
                    "<div class='colours'>" + "".join(
            f"<a class='colour' href='/produce/{p['slug']}/{v['slug']}/'>"
            f"<img src='/assets/{v['crate']}.webp' alt='Crate of {html.escape(v['name'].lower())}' loading='lazy'>"
            f"<h3>{html.escape(v['name'])}</h3>"
            f"<p class='sm'>{html.escape(v['blurb'])}</p>"
            f"<span class='go'>See this type &#8594;</span></a>"
            for v in p["variants"]) + "</div></section>")

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

{variants}

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


def variant_page(parent, v):
    url = f"{SITE}/produce/{parent['slug']}/{v['slug']}/"
    body = f"""<main class='prod'>
<p class='crumb'><a href='/produce/'>Produce</a> &#8250; <a href='/produce/{parent['slug']}/'>{html.escape(parent['name'])}</a> &#8250; <span>{html.escape(v['name'])}</span></p>
<div class='phero'>
  <div>
    <p class='kick'>{html.escape(parent['tag'])} &#183; Brazil</p>
    <h1>{html.escape(v['name'])}</h1>
    <p class='lede'>{html.escape(v['blurb'])}</p>
    <div class='bcta'>
      <a class='bbtn solid' href='{WA_US}' target='_blank' rel='noopener'>Ask about {html.escape(v['name'].lower())}</a>
      <a class='bbtn' href='mailto:trade@terrafrescatrading.com'>Request a quote</a>
    </div>
  </div>
  <img class='pcrate' src='/assets/{v['crate']}.webp' alt='Crate of {html.escape(v['name'].lower())}'>
</div>
<section class='pblock'><h2>Varieties</h2>
  <ul class='pills'>{"".join(f"<li>{html.escape(x)}</li>" for x in v['varieties'])}</ul></section>
<section class='pblock'><h2>Availability through the year</h2>
  {calendar(parent['peak'], parent['available'])}</section>
<section class='pblock'><h2>Where it grows</h2>
  <ul class='pills alt'>{"".join(f"<li>{html.escape(x)}</li>" for x in parent['states'])}</ul>
  <p class='sm'>{html.escape(D.REACH_NOTE)}</p></section>
<section class='pblock'><h2>What matters on this type</h2><p>{html.escape(v['notes'])}</p></section>
<section class='pblock volume'><h2>Volume and packing</h2>
  <p>Volume is agreed per programme rather than quoted from a list. Tell us the weekly quantity,
  the calibre and the format you need, and the window you need it in.</p>
  <div class='bcta'><a class='bbtn solid' href='{WA_US}' target='_blank' rel='noopener'>Tell us your programme</a></div>
</section>
<nav class='pnext'><h2>Other {html.escape(parent['name'].lower())} types</h2><div class='cards'>{"".join(
  f"<a class='card' href='/produce/{parent['slug']}/{o['slug']}/'><span class='kick'>{html.escape(parent['tag'])}</span>"
  f"<h2>{html.escape(o['name'])}</h2><p>{html.escape(o['blurb'])}</p></a>"
  for o in parent['variants'] if o['slug'] != v['slug'])}</div></nav>
</main>"""
    desc = f"{v['name']} from Brazil — {', '.join(v['varieties'][:3])}. {v['blurb']}"
    d = ROOT / "produce" / parent["slug"] / v["slug"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(
        shell(f"{v['name']} from Brazil — varieties and season | Terra Fresca",
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



# ---------------------------------------------------------------- standalone
SERVICES = [('Fresh sourcing', 'We buy at the farm gate, not on the open market.', "We represent farms across Brazil and build the supply base around the programme rather than around one estate's capacity. That means naming the farms supplying you, giving you their GLOBALG.A.P. number so you can verify it yourself, and agreeing variety, calibre and brix as a specification rather than a hope."), ('Cold chain', 'Pre-cooling is the job, not an optimisation.', 'A reefer circulates air at a set temperature; it does not pull heat out of warm fruit. Pulp temperature is logged at loading and set-point through the voyage, and the download comes with the shipment rather than on request. Set-points are specified per programme — variety, maturity and transit time all move the right number.'), ('Ocean and air freight', 'Weekly reefer capacity, and air when the window is short.', 'We ship out of Santos, Itajai, Pecem and Natal and choose the port against the packhouse, not against habit — northeastern fruit going to Europe should not spend two days on a truck to Santos first. Same-week air lift via GRU for the lines and windows where a vessel will not make it.'), ('Customs and documentation', 'MAPA certification handled in-house, checked against the destination.', "Phytosanitary certification, additional declaration wording, certificate of origin and destination compliance sit with the same team that sourced the fruit. The document set is reviewed against your broker's requirements before the container loads rather than after it arrives.")]


def simple(slug, title, desc, body):
    d = ROOT / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(
        shell(title, desc, f"{SITE}/{slug}/", body), encoding="utf-8")


def services_page():
    blocks = "".join(
        f"<section class='pblock srv'><p class='kick'>0{i+1} / 04</p><h2>{html.escape(n)}</h2>"
        f"<p class='lede'>{html.escape(t)}</p><p>{html.escape(b)}</p></section>"
        for i, (n, t, b) in enumerate(SERVICES))
    body = ("<div class='masthead'><div class='mwrap'><p class='kick'>Terra Fresca &#183; Services</p>"
            "<h1>One accountable team, farm gate to your dock</h1>"
            "<p class='lede'>We are a trading house, not a carrier and not a broker. We buy the fruit, "
            "own the container, run the cold chain and the paperwork, and sell to you on one invoice.</p>"
            "</div></div>"
            f"<main class='prod'>{blocks}"
            "<section class='pblock volume'><h2>Who owns the fruit while it is on the water?</h2>"
            "<p>That one question separates a trading house from a broker. If the answer is "
            "&#8216;the grower&#8217; or &#8216;it depends&#8217;, you are carrying the risk. "
            "We buy at the farm gate, so we are not indifferent to how it arrives.</p>"
            "<div class='bcta'><a class='bbtn solid' href='/contact/'>Talk to us</a>"
            "<a class='bbtn' href='/blog/what-a-trading-house-actually-does/'>Read more</a></div>"
            "</section></main>")
    simple("services", "Services — sourcing, cold chain, freight and customs | Terra Fresca",
           "Fresh sourcing from named Brazilian farms, a logged cold chain, weekly reefer capacity "
           "out of four ports plus air freight, and MAPA certification handled in-house.", body)


def about_page():
    body = ("<div class='masthead'><div class='mwrap'><p class='kick'>Terra Fresca &#183; About</p>"
            "<h1>Fifteen years in the same valleys</h1>"
            "<p class='lede'>Terra Fresca Trading has been buying and moving Brazilian produce for "
            "over fifteen years, with more than thirty partner farms and retail operations across "
            "Minas Gerais and S&#227;o Paulo.</p></div></div>"
            "<main class='prod'>"
            "<div class='pgrid'>"
            "<section class='pblock'><h2>What we are</h2>"
            "<p>A produce trading house. We buy fruit and vegetables directly from certified "
            "Brazilian growers, take ownership of every container we move, run the cold chain and "
            "the export paperwork ourselves, and sell wholesale to importers, distributors and "
            "retail chains worldwide.</p>"
            "<p>The grower is paid for the fruit. You buy from one seller, on one invoice, with one "
            "team answerable for it.</p></section>"
            "<section class='pblock'><h2>What that changes</h2>"
            "<p>A broker introduces you to a grower and takes a commission. When the container "
            "arrives warm, they are not a party to the sale.</p>"
            "<p>Because we have already paid for the fruit, there is no version of this where we are "
            "indifferent to how it arrives. That is the whole argument for the model.</p></section>"
            "</div>"
            "<section class='pblock'><h2>Where we are</h2>"
            "<div class='pgrid'>"
            "<div><p class='kick'>Brazil</p><p>Av. Pres. Ant&#244;nio Carlos, 4048 &#8212; Pampulha<br>"
            "Belo Horizonte &#8212; MG, 31270-000<br><a href='https://wa.me/5531987770220' "
            "target='_blank' rel='noopener'>WhatsApp +55 31 98777-0220</a></p></div>"
            "<div><p class='kick'>United States</p><p>433 Plaza Real, Suite 275<br>"
            "Boca Raton, FL 33432<br><a href='https://wa.me/19543523599' target='_blank' "
            "rel='noopener'>WhatsApp +1 954 352 3599</a></p></div></div></section>"
            "<section class='pblock volume'><h2>Start a programme</h2>"
            "<p>Tell us the line, the weekly volume, the format and the window. We will tell you "
            "what Brazil can actually deliver against it.</p>"
            "<div class='bcta'><a class='bbtn solid' href='/contact/'>Contact us</a>"
            "<a class='bbtn' href='/produce/'>See the produce</a></div></section></main>")
    simple("about", "About Terra Fresca Trading — a Brazilian produce trading house",
           "Over fifteen years trading Brazilian fresh produce, with more than thirty partner farms "
           "and retail across Minas Gerais and Sao Paulo. Offices in Belo Horizonte and Boca Raton.", body)


def contact_page():
    body = ("<div class='masthead'><div class='mwrap'><p class='kick'>Terra Fresca &#183; Contact</p>"
            "<h1>Tell us what you need and when</h1>"
            "<p class='lede'>The fastest route is WhatsApp. If you can include the line, the weekly "
            "volume, the format and the window you need it in, we can usually answer the same day.</p>"
            "</div></div>"
            "<main class='prod'>"
            "<div class='pgrid'>"
            "<section class='pblock'><h2>Brazil</h2>"
            "<p>Av. Pres. Ant&#244;nio Carlos, 4048 &#8212; Pampulha<br>Belo Horizonte &#8212; MG<br>31270-000</p>"
            "<div class='bcta'><a class='bbtn solid' href='https://wa.me/5531987770220' target='_blank' "
            "rel='noopener'>WhatsApp +55 31 98777-0220</a></div></section>"
            "<section class='pblock'><h2>United States</h2>"
            "<p>433 Plaza Real, Suite 275<br>Boca Raton, FL 33432</p>"
            "<div class='bcta'><a class='bbtn solid' href='" + WA_US + "' target='_blank' "
            "rel='noopener'>WhatsApp +1 954 352 3599</a></div></section></div>"
            "<section class='pblock'><h2>By email</h2>"
            "<p><a href='mailto:trade@terrafrescatrading.com'>trade@terrafrescatrading.com</a><br>"
            "Monday to Friday, 8:00&#8211;18:00 BRT</p></section>"
            "<section class='pblock volume'><h2>What to include</h2>"
            "<p>An enquiry we can answer immediately usually has four things in it:</p>"
            "<ul class='pills alt'><li>The line and variety</li><li>Weekly volume</li>"
            "<li>Pack format and calibre</li><li>The window and destination port</li></ul>"
            "<p class='sm'>If you are not sure on format or calibre, say so &#8212; that is a "
            "conversation, not a blocker.</p></section></main>")
    simple("contact", "Contact Terra Fresca Trading — Brazil and United States",
           "Talk to Terra Fresca on WhatsApp or by email. Offices in Belo Horizonte, Minas Gerais "
           "and Boca Raton, Florida.", body)


def main():
    n = 0
    for p in D.PRODUCTS:
        product_page(p)
        for v in p.get("variants", []):
            variant_page(p, v); n += 1
    index_page()
    services_page()
    about_page()
    contact_page()
    print(f"produce: {len(D.PRODUCTS)} product pages, {n} type pages, + index")


if __name__ == "__main__":
    main()
