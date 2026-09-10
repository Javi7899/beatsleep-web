"""The seven languages, in one place.

`code` is the BCP-47 tag and the folder name. English is the root, so its
folder is empty. `name` is the endonym: a language names itself, in every
language, which is also why the switcher needs no translating.
"""

LANGS = [
    {"code": "en",    "dir": "",       "name": "English",    "og": "en_US", "badge": "en"},
    {"code": "es",    "dir": "es/",    "name": "Español",    "og": "es_ES", "badge": "es"},
    {"code": "fr",    "dir": "fr/",    "name": "Français",   "og": "fr_FR", "badge": "fr"},
    {"code": "de",    "dir": "de/",    "name": "Deutsch",    "og": "de_DE", "badge": "de"},
    {"code": "it",    "dir": "it/",    "name": "Italiano",   "og": "it_IT", "badge": "it"},
    {"code": "pt-BR", "dir": "pt-br/", "name": "Português",  "og": "pt_BR", "badge": "pt-br"},
    {"code": "ja",    "dir": "ja/",    "name": "日本語",       "og": "ja_JP", "badge": "ja"},
]

BY_CODE = {l["code"]: l for l in LANGS}
SITE = "https://javi7899.github.io/beatsleep-web/"
PAGES = ["index", "privacy", "support", "terms"]


def path(lang, page):
    """Where a page lives, relative to the site root."""
    return lang["dir"] + ("" if page == "index" else f"{page}.html")


def file(lang, page):
    """Where a page is written on disk. The URL may end in a slash; a file
    may not."""
    return lang["dir"] + f"{page}.html" if page != "index" else lang["dir"] + "index.html"


def base(lang):
    """How a page in this language reaches the site root."""
    return "" if lang["code"] == "en" else "../"
