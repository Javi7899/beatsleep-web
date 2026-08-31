#!/usr/bin/env python3
"""Re-wraps the text pages in the site's chrome.

The masthead and the footer are the same on every page and were pasted into
each of them; when the chrome changed, six files had to change with it. This
takes the <main> out of a page and puts it back inside the current chrome, so
the pasting is done by a script that cannot forget one.

    python3 tools/rewrap.py
"""

import re, sys, os

BASE = "https://javi7899.github.io/beatsleep-web/"

WORDS = {
    "en": dict(skip="Skip to content", how="How it works", privacy="Privacy",
               support="Support", other="Español", get="Get it",
               store="On the App Store", legal="Legal", lang="Language",
               write="Write to me", terms="Terms of use",
               policy="Privacy policy", other_lang="es", other_code="es",
               home="Home",
               colophon="This site has no cookies, no analytics and no third-party requests."),
    "es": dict(skip="Ir al contenido", how="Cómo funciona", privacy="Privacidad",
               support="Soporte", other="English", get="Descargar",
               store="En el App Store", legal="Legal", lang="Idioma",
               write="Escríbeme", terms="Condiciones de uso",
               policy="Política de privacidad", other_lang="en", other_code="en",
               home="Inicio",
               colophon="Este sitio no tiene cookies, ni analítica, ni peticiones a terceros."),
}

def head(lang, title, desc, path, alt_path, prefix):
    w = WORDS[lang]
    locale = "es_ES" if lang == "es" else "en"
    alt_locale = "en" if lang == "es" else "es_ES"
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#000000">
<link rel="canonical" href="{BASE}{path}">
<meta property="og:site_name" content="BeatSleep">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:image" content="{BASE}assets/mark.png">
<meta property="og:locale" content="{locale}">
<meta property="og:locale:alternate" content="{alt_locale}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{prefix}assets/icon-180.png">
<link rel="apple-touch-icon" href="{prefix}assets/icon-180.png">
<link rel="alternate" hreflang="{w['other_code']}" href="{BASE}{alt_path}">
<link rel="alternate" hreflang="{lang}" href="{BASE}{path}">
<link rel="stylesheet" href="{prefix}style.css">
<script>document.documentElement.classList.add('js')</script>
</head>
<body>
<div class="wrap">
<a class="skip" href="#main">{w['skip']}</a>
'''

def mast(lang, prefix, here, other_href):
    w = WORDS[lang]
    def link(href, label, key, extra=""):
        cur = ' aria-current="page"' if key == here else ""
        return f'    <a{extra} href="{href}"{cur}>{label}</a>\n'
    home = prefix if prefix else "./"
    out = f'''<header class="mast">
  <a class="home" href="{home}"><img src="{prefix}assets/mark-120.png" alt=""><span>BeatSleep</span></a>
  <nav>
'''
    out += link("privacy.html", w["privacy"], "privacy")
    out += link("support.html", w["support"], "support")
    out += f'    <a href="{other_href}" hreflang="{w["other_code"]}" lang="{w["other_code"]}">{w["other"]}</a>\n'
    out += f'    <a class="get" href="https://apps.apple.com/app/id6805001777">{w["get"]}</a>\n'
    out += '  </nav>\n</header>\n'
    return out

def foot(lang, prefix, other_href):
    w = WORDS[lang]
    home = prefix if prefix else "./"
    return f'''<footer>
  <div class="footer-inner">
    <div>
      <h2>BeatSleep</h2>
      <ul>
        <li><a href="{home}">{w['home']}</a></li>
        <li><a href="https://apps.apple.com/app/id6805001777">{w['store']}</a></li>
        <li><a href="support.html">{w['support']}</a></li>
      </ul>
    </div>
    <div>
      <h2>{w['legal']}</h2>
      <ul>
        <li><a href="privacy.html">{w['policy']}</a></li>
        <li><a href="terms.html">{w['terms']}</a></li>
      </ul>
    </div>
    <div>
      <h2>{w['lang']}</h2>
      <ul>
        <li><a href="{other_href}" hreflang="{w['other_code']}" lang="{w['other_code']}">{w['other']}</a></li>
      </ul>
    </div>
    <div>
      <h2>{w['write']}</h2>
      <ul>
        <li><a href="mailto:beatsleepf@gmail.com">beatsleepf@gmail.com</a></li>
      </ul>
    </div>
  </div>
  <div class="colophon">
    <span class="mark"><img src="{prefix}assets/mark-120.png" alt="">© 2026 Javier Torres Rubio</span>
    <span class="spacer"></span>
    <span>{w['colophon']}</span>
  </div>
</footer>
</div>
<script src="{prefix}app.js" defer></script>
</body>
</html>
'''

PAGES = [
    # file, lang, key, title, description
    ("support.html", "en", "support", "BeatSleep — Support",
     "Help with BeatSleep: the taps, the night, your data and the subscription. Written by a person, answered by a person."),
    ("es/support.html", "es", "support", "BeatSleep — Soporte",
     "Ayuda con BeatSleep: los toques, la noche, tus datos y la suscripción. Lo escribe una persona y lo contesta una persona."),
    ("privacy.html", "en", "privacy", "BeatSleep — Privacy Policy",
     "BeatSleep collects nothing. No account, no server, no analytics: what it reads stays on your own devices."),
    ("terms.html", "en", "terms", "BeatSleep — Terms of Use",
     "The terms of use for BeatSleep and BeatSleep Pro."),
    ("es/privacy.html", "es", "privacy", "BeatSleep — Política de privacidad",
     "BeatSleep no recoge nada. Sin cuenta, sin servidor y sin analítica: lo que lee se queda en tus propios dispositivos."),
    ("es/terms.html", "es", "terms", "BeatSleep — Condiciones de uso",
     "Las condiciones de uso de BeatSleep y BeatSleep Pro."),
]

def main():
    for path, lang, key, title, desc in PAGES:
        src = open(path).read()
        body = re.search(r"<main[^>]*>(.*)</main>", src, re.S).group(1).strip()
        prefix = "../" if lang == "es" else ""
        rel = path.split("/")[-1]
        page = ("es/" + rel) if lang == "es" else rel
        alt = rel if lang == "es" else ("es/" + rel)
        other_href = (prefix + rel) if lang == "es" else ("es/" + rel)
        out = (head(lang, title, desc, page, alt, prefix)
               + mast(lang, prefix, key, other_href)
               + '<main id="main" class="page narrow">\n' + body + "\n</main>\n"
               + foot(lang, prefix, other_href))
        open(path, "w").write(out)
        print("rewrapped", path)

if __name__ == "__main__":
    main()
