# beatsleep.web

The public site for **BeatSleep**: what the app is, the privacy policy, the
support page and the terms of use that the App Store listing points at.

Static HTML, no build step, no framework, no analytics and no third-party
request of any kind. The palette and the type are the app's own: black ground,
nothing above 92% white, accent at OKLCH hue 282.

```
index.html      what the app is           es/index.html
privacy.html    privacy policy            es/privacy.html
support.html    support and FAQ           es/support.html
terms.html      terms of use              es/terms.html
style.css       the whole design system, one file
app.js          two behaviours: the sticky masthead, and the reveals
```

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
