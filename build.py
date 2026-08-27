#!/usr/bin/env python3
"""Build index.html from index.src.html.

Two modes:

  python3 build.py            → assets referenced as files  (the website)
  python3 build.py --inline   → assets embedded as data URIs (offline one-filer)

The "embed everything, zero external refs" rule exists so a brand book or a deck
can be emailed and still open on a phone with no network. The website is not
that: it is served by Cloudflare, which already hosts assets/ at 200 and caches
each file independently. Inlining there cost a 6.5 MB index.html of which only
250 KB was actually the page — the rest was payload the browser had to swallow
before it could draw anything, re-downloaded in full on every deploy, with a
~33% base64 tax on top.

  <!--INLINE_JS path-->  becomes an inline <script> (always inlined: it is small
                         and the page cannot start without it)
  {{A:name}}             assets/name.webp
  {{V:name}}             assets/name.mp4
  {{FRAMES:name}}        JS array of assets/seq/name/*.webp
  {{LAND}}               always inlined — it is a base64 string inside JS
"""
import base64, pathlib, re, sys

root = pathlib.Path(__file__).parent
INLINE = "--inline" in sys.argv
src = (root / "index.src.html").read_text()

# The source keeps the previous scene implementation as a readable reference,
# but production ships only the continuous master-film version. Strip legacy
# markup before asset handling so duplicate video/image data is never emitted.
src = re.sub(r"<!--LEGACY_HTML_START-->.*?<!--LEGACY_HTML_END-->", "", src, flags=re.S)
src = re.sub(r"/\*LEGACY_JS_START\*/.*?/\*LEGACY_JS_END\*/", "", src, flags=re.S)


def inline_js(m):
    return "<script>\n" + (root / m.group(1)).read_text() + "\n</script>"


src = re.sub(r"<!--INLINE_JS ([\w./-]+)-->", inline_js, src)


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def asset(m):
    p = root / "assets" / (m.group(1) + ".webp")
    if not p.exists():
        raise SystemExit(f"build: missing asset {p}")
    return data_uri(p, "image/webp") if INLINE else f"assets/{p.name}"


def video(m):
    p = root / "assets" / (m.group(1) + ".mp4")
    if not p.exists():
        raise SystemExit(f"build: missing video {p}")
    return data_uri(p, "video/mp4") if INLINE else f"assets/{p.name}"


def frames(m):
    d = root / "assets" / "seq" / m.group(1)
    if not d.is_dir():
        return "[]"
    fs = sorted(d.glob("*.webp"))
    if INLINE:
        return "[" + ",".join('"' + data_uri(f, "image/webp") + '"' for f in fs) + "]"
    return "[" + ",".join(f'"assets/seq/{m.group(1)}/{f.name}"' for f in fs) + "]"


src = re.sub(r"\{\{A:([\w-]+)\}\}", asset, src)
src = re.sub(r"\{\{V:([\w-]+)\}\}", video, src)
src = re.sub(r"\{\{FRAMES:([\w-]+)\}\}", frames, src)
src = src.replace("{{LAND}}", (root / "assets" / "landbits.txt").read_text().strip())

out = root / "index.html"
out.write_text(src)
kb = out.stat().st_size / 1024
print(f"built index.html: {kb:.0f} KB  ({'inlined' if INLINE else 'referenced'})")
