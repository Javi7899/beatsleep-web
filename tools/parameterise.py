"""Turn the four templates from English pages into language-agnostic ones.

Run once. Everything it replaces is chrome: the tag on <html>, the canonical
and alternate links, the asset paths, the store badge and the two language
switchers. The words are already tokens by now; these are the parts that
change with the language without being translated.
"""
import re
from pathlib import Path

PAGES = ["index", "privacy", "support", "terms"]

for page in PAGES:
    p = Path(f"templates/{page}.html")
    h = p.read_text()

    h = h.replace('<html lang="en">', '<html lang="{{@lang}}">')

    # The canonical, the og:url and the whole alternate block are generated,
    # because with seven languages they are seven lines that must agree.
    h = re.sub(r'<link rel="canonical" href="[^"]*">', '{{@canonical}}', h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">',
               '<meta property="og:url" content="{{@url}}">', h)
    h = re.sub(r'<meta property="og:locale" content="[^"]*">\n'
               r'<meta property="og:locale:alternate" content="[^"]*">',
               '{{@oglocales}}', h)
    h = re.sub(r'(?:<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n)+',
               '{{@alternates}}\n', h)

    # Assets are reached from the root, and a page in a folder is one level in.
    h = re.sub(r'(?<=src=")assets/', '{{@base}}assets/', h)
    h = re.sub(r'(?<=href=")assets/', '{{@base}}assets/', h)
    h = h.replace('href="style.css"', 'href="{{@base}}style.css"')
    h = h.replace('src="app.js"', 'src="{{@base}}app.js"')
    h = h.replace('badge-en.svg', 'badge-{{@badge}}.svg')

    # Two switchers: one in the masthead, one in the footer.
    h = re.sub(r'\n\s*<a href="es/[^"]*" hreflang="es" lang="es">\{\{Español\}\}</a>',
               '\n{{@navlang}}', h)
    h = re.sub(r'\s*<li>\{\{<a href="es/[^"]*" hreflang="es" lang="es">Español</a>\}\}</li>',
               '\n{{@footerlangs}}', h)

    p.write_text(h)
    left = re.findall(r'\bes/|badge-en|lang="en"', h)
    tokens = len(re.findall(r"\{\{@", h))
    note = "  LEFTOVER " + str(left) if left else ""
    print(f"{page}: {tokens} chrome tokens{note}")
