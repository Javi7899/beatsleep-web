"""Put the templates and the content back together, in seven languages.

    python3 tools/build.py

Writes every page of the site. The words come from `content/<code>.json`,
keyed by the English string; a key with no translation falls back to the
English rather than to an empty page, and the run says how many did.
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from langs import LANGS, BY_CODE, SITE, PAGES, path, file, base

TOKEN = re.compile(r"\{\{(.*?)\}\}", re.S)


def switcher(lang, page):
    """The masthead's language menu: a disclosure, so it needs no script."""
    others = "".join(
        f'\n      <li><a href="{base(lang)}{path(other, page)}" '
        f'hreflang="{other["code"]}" lang="{other["code"]}">{other["name"]}</a></li>'
        for other in LANGS if other["code"] != lang["code"])
    return (f'    <details class="lang">\n'
            f'      <summary aria-label="Language">{lang["name"]}</summary>\n'
            f'      <ul>{others}\n      </ul>\n'
            f'    </details>')


def footer_langs(lang, page):
    return "\n".join(
        f'        <li><a href="{base(lang)}{path(other, page)}" '
        f'hreflang="{other["code"]}" lang="{other["code"]}">{other["name"]}</a></li>'
        for other in LANGS if other["code"] != lang["code"])


def alternates(page):
    rows = [f'<link rel="alternate" hreflang="{l["code"]}" href="{SITE}{path(l, page)}">'
            for l in LANGS]
    rows.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}{path(BY_CODE["en"], page)}">')
    return "\n".join(rows)


def oglocales(lang):
    rows = [f'<meta property="og:locale" content="{lang["og"]}">']
    rows += [f'<meta property="og:locale:alternate" content="{o["og"]}">'
             for o in LANGS if o["code"] != lang["code"]]
    return "\n".join(rows)


def render(page, lang, words):
    template = Path(f"templates/{page}.html").read_text()
    url = SITE + path(lang, page)
    # Apple ships its own badge per language and it is their artwork, not
    # something to redraw. Until a language's badge has been fetched from
    # Apple's marketing tools, that language shows the English one rather than
    # a broken image.
    badge = lang["badge"] if Path(f"assets/badge-{lang['badge']}.svg").exists() else "en"
    chrome = {
        "@lang": lang["code"],
        "@base": base(lang),
        "@badge": badge,
        "@url": url,
        "@canonical": f'<link rel="canonical" href="{url}">',
        "@alternates": alternates(page),
        "@oglocales": oglocales(lang),
        "@navlang": switcher(lang, page),
        "@footerlangs": footer_langs(lang, page),
    }
    missing = []

    def one(m):
        key = m.group(1)
        if key.startswith("@"):
            return chrome[key]
        if key in words:
            return words[key]
        missing.append(key)
        return key

    out = TOKEN.sub(one, template)
    return out, missing


if __name__ == "__main__":
    total_missing = 0
    for lang in LANGS:
        words = {}
        source = Path(f"content/{lang['code']}.json")
        if source.exists():
            words = json.loads(source.read_text())
        gaps = set()
        for page in PAGES:
            html, missing = render(page, lang, words)
            gaps.update(missing)
            out = Path(file(lang, page))
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html)
        total_missing += len(gaps)
        state = "complete" if not gaps else f"{len(gaps)} still in English"
        print(f"  {lang['code']:<6} {lang['name']:<10} {state}")
    print(f"{len(LANGS) * len(PAGES)} pages written"
          + (f", {total_missing} untranslated strings in all" if total_missing else ""))
