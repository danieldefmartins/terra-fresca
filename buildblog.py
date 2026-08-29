#!/usr/bin/env python3
"""Build the blog from Markdown.

  blog/posts/<slug>.md  ->  blog/<slug>/index.html
                            blog/index.html
                            sitemap.xml   (home + every article)

Each post starts with a small frontmatter block:

    ---
    title: ...
    description: ...      <- becomes the meta description and the card blurb
    date: 2026-08-29      <- ISO, used for ordering and for schema
    tag: Cold chain
    ---

Only the Markdown this site actually uses is supported — headings, paragraphs,
lists, tables, bold/italic, links, blockquotes. That is deliberate: a tiny
converter with no dependencies is easier to trust than a general one, and the
articles are written to fit it.
"""
import html, pathlib, re, datetime

ROOT = pathlib.Path(__file__).parent
POSTS = ROOT / "blog" / "posts"
SITE = "https://terra-fresca.danieldefmartins.workers.dev"
WA_US = ("https://wa.me/19543523599?text=Hi%20Terra%20Fresca%20%E2%80%94%20I%27d%20like%20to"
         "%20talk%20about%20sourcing%20fruit%20from%20Brazil.")


# ----------------------------------------------------------------- markdown
ITEM = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def to_html(md):
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:])}</h3>"); i += 1
        elif ln.startswith("## "):
            out.append(f"<h2>{inline(ln[3:])}</h2>"); i += 1
        elif ln.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith("> "):
                buf.append(inline(lines[i][2:])); i += 1
            out.append("<blockquote><p>" + " ".join(buf) + "</p></blockquote>")
        elif ITEM.match(ln):
            tag = "ol" if re.match(r"^\s*\d+\.\s", ln) else "ul"
            buf = []
            while i < len(lines) and ITEM.match(lines[i]):
                buf.append("<li>" + inline(ITEM.sub("", lines[i])) + "</li>")
                i += 1
            out.append(f"<{tag}>" + "".join(buf) + f"</{tag}>")
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], [r for r in rows[1:] if not set("".join(r)) <= set("-: ")]
            t = "<div class='tw'><table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            for r in body:
                t += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
            out.append(t + "</tbody></table></div>")
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "-", ">", "|")):
                buf.append(inline(lines[i])); i += 1
            out.append("<p>" + " ".join(buf) + "</p>")
    return "\n".join(out)


def read_post(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        raise SystemExit(f"blog: {path.name} has no frontmatter block")
    meta = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    meta["slug"] = path.stem
    meta["body"] = m.group(2).strip()
    for need in ("title", "description", "date"):
        if need not in meta:
            raise SystemExit(f"blog: {path.name} is missing '{need}'")
    return meta


# ------------------------------------------------------------------ shell
def shell(title, desc, canonical, body, extra_ld=""):
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
<meta property="og:type" content="article">
<meta property="og:site_name" content="Terra Fresca Trading">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/blog/blog.css">
{extra_ld}
</head>
<body>
<header class="bhead">
  <a class="blogo" href="/"><b>TERRA FRESCA</b><i>Global Produce Trading</i></a>
  <nav><a href="/">Home</a><a href="/blog/">Journal</a><a href="/#cta">Contact</a></nav>
</header>
{body}
<footer class="bfoot">
  <div>
    <p class="tag">From Brazilian soil. To tables worldwide.</p>
    <p class="sm">Terra Fresca Trading — Belo Horizonte, MG · Boca Raton, FL</p>
  </div>
  <div class="bcta">
    <a class="bbtn solid" href="{WA_US}" target="_blank" rel="noopener">WhatsApp us</a>
    <a class="bbtn" href="mailto:trade@terrafrescatrading.com">Request a quote</a>
  </div>
</footer>
</body>
</html>
"""


def main():
    posts = sorted((read_post(p) for p in POSTS.glob("*.md")),
                   key=lambda m: m["date"], reverse=True)
    if not posts:
        raise SystemExit("blog: no posts found in blog/posts/")

    for p in posts:
        url = f"{SITE}/blog/{p['slug']}/"
        ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article",'
              f'"headline":{html.escape(p["title"])!r},'.replace("'", '"') +
              f'"description":"{html.escape(p["description"])}","datePublished":"{p["date"]}",'
              f'"mainEntityOfPage":"{url}",'
              '"author":{"@type":"Organization","name":"Terra Fresca Trading"},'
              '"publisher":{"@type":"Organization","name":"Terra Fresca Trading"}}</script>')
        body = (f"<main class='post'><article>"
                f"<p class='kick'>{html.escape(p.get('tag','Journal'))} · "
                f"{datetime.date.fromisoformat(p['date']).strftime('%d %B %Y')}</p>"
                f"<h1>{html.escape(p['title'])}</h1>"
                f"<p class='lede'>{html.escape(p['description'])}</p>"
                f"{to_html(p['body'])}"
                "<hr><p class='sm'>Terra Fresca Trading buys at the farm gate and sells at your dock. "
                "Regulatory detail changes — confirm current requirements with the relevant authority "
                "before you ship.</p>"
                "</article>"
                "<aside class='more'><h2>More from the journal</h2><ul>" +
                "".join(f"<li><a href='/blog/{o['slug']}/'>{html.escape(o['title'])}</a></li>"
                        for o in posts if o["slug"] != p["slug"])
                + "</ul></aside></main>")
        d = ROOT / "blog" / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(shell(p["title"] + " — Terra Fresca Trading",
                                            p["description"], url, body, ld), encoding="utf-8")

    cards = "".join(
        f"<a class='card' href='/blog/{p['slug']}/'>"
        f"<span class='kick'>{html.escape(p.get('tag','Journal'))}</span>"
        f"<h2>{html.escape(p['title'])}</h2><p>{html.escape(p['description'])}</p>"
        f"<span class='sm'>{datetime.date.fromisoformat(p['date']).strftime('%d %B %Y')}</span></a>"
        for p in posts)
    idx_body = ("<main class='index'><p class='kick'>Journal</p>"
                "<h1>Notes from the cold chain</h1>"
                "<p class='lede'>What we have learned buying fruit at the farm gate in Brazil and "
                "landing it on docks around the world — seasons, temperatures, paperwork and ports.</p>"
                f"<div class='cards'>{cards}</div></main>")
    (ROOT / "blog" / "index.html").write_text(
        shell("Journal — Terra Fresca Trading",
              "Practical notes on exporting Brazilian fruit and vegetables: harvest calendars, reefer "
              "set-points, phytosanitary paperwork, load ports and import requirements.",
              f"{SITE}/blog/", idx_body), encoding="utf-8")

    urls = [(f"{SITE}/", "1.0", None), (f"{SITE}/blog/", "0.8", None)]
    urls += [(f"{SITE}/blog/{p['slug']}/", "0.7", p["date"]) for p in posts]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemap.org/schemas/sitemap/0.9">'.replace("sitemap.org", "sitemaps.org")]
    for loc, pri, lastmod in urls:
        sm.append("  <url><loc>" + loc + "</loc>"
                  + (f"<lastmod>{lastmod}</lastmod>" if lastmod else "")
                  + f"<priority>{pri}</priority></url>")
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    print(f"blog: {len(posts)} articles + index, sitemap with {len(urls)} urls")


if __name__ == "__main__":
    main()
