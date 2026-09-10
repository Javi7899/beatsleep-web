# beatsleep.web

The public site for **BeatSleep**: what the app is, the privacy policy, the
support page and the terms of use that the App Store listing points at.

Static HTML, no build step, no framework, no analytics and no third-party
request of any kind. The palette and the type are the app's own: black ground,
nothing above 92% white, accent at OKLCH hue 282.

```
templates/*.html   the markup, with every string as a {{token}}
content/<lang>.json  the words, keyed by the English string
tools/langs.py     the seven languages, in one place
tools/build.py     puts them together and writes all 28 pages
style.css          the whole design system, one file
app.js             two behaviours: the sticky masthead, and the reveals
```

## The seven languages

The site is English, Spanish, French, German, Italian, Brazilian Portuguese and
Japanese: the same seven the app is read in. Seven hand-written copies of the
same page is six copies that drift, so **no page is edited directly**. Every
`.html` at the root and in `en/ es/ fr/ de/ it/ pt-br/ ja/` is written by:

```
python3 tools/build.py
```

Editing the words means editing `content/<lang>.json`. Editing the markup means
editing `templates/`. A key with no translation yet falls back to English and
the build says how many did, so a half-translated language is a working page
rather than a broken one.

**Changing an English string is a rename**, because the key is the English:

```
python3 tools/rekey.py "the old sentence" "the new sentence"
```

That moves the token in the templates and the key in all seven content files at
once, so no translation is orphaned.

`tools/extract.py` is how the templates were made in the first place, out of
the hand-written English pages. It is kept for the next page rather than for
daily use.

**The store badge** is Apple's artwork and there is one per language. Only
`badge-en.svg` and `badge-es.svg` are here; any language without its own shows
the English one rather than a broken image, so a badge dropped into `assets/`
is picked up on the next build with no other change.

## The figures

Every chart on the home page is drawn by `tools/figures.py` into
`assets/figures/*.svg`: the Nightprint, the hypnogram, the ten-week calendar
and the descent. They are **not** screenshots of the app and not anybody's
data: one made-up night, run through the app's own rules, so the shapes stay
honest. Re-run after editing that file:

```
python3 tools/figures.py
```

## The chrome

The masthead and the footer are identical on the six text pages, so they are
not maintained by hand. Edit `tools/rewrap.py` and run it; it lifts each page's
`<main>` out and puts it back inside the current chrome.

```
python3 tools/rewrap.py
```

`index.html` and `es/index.html` are written out in full and are not touched by
that script, because the home page has a masthead of its own, with the anchors.

## Publishing

Served by GitHub Pages from `main`. Editing a file and pushing publishes it.
