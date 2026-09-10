"""Pull the copy out of a page and leave a template behind.

The site is seven languages now, and seven hand-written copies of the same
page is six copies that drift. So each page is split once into a template,
which is the markup, and a content file, which is the words. `build.py` puts
them back together.

The keys are the English strings themselves, exactly as the app's own string
catalogue does it: a key that is the sentence cannot be mapped to the wrong
sentence, and a translator reading the file sees what they are translating.
"""
import json, re, sys
from pathlib import Path

# Elements whose inside is one thing to translate, markup and all. A sentence
# with a <strong> in the middle is one sentence, not three fragments.
LEAF = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "span", "a", "td", "th",
        "figcaption", "dt", "dd", "button", "summary", "label", "title", "text"}
# Everything a leaf may contain and still be a leaf.
INLINE = {"strong", "em", "b", "i", "span", "a", "br", "code", "abbr", "small",
          "sup", "sub", "wbr", "nobr"}
SKIP = {"script", "style", "svg", "path", "defs", "g", "circle", "rect", "line",
        "polyline", "polygon", "use", "symbol", "clippath", "lineargradient", "stop"}
VOID = {"img", "br", "input", "meta", "link", "hr", "source", "wbr", "col"}

TAG = re.compile(r"<(/?)([a-zA-Z][-a-zA-Z0-9]*)((?:\"[^\"]*\"|'[^']*'|[^>\"'])*?)(/?)>")
ATTRS = {"alt", "aria-label", "title", "placeholder"}


def spans(html: str):
    """Every (start, end) of the source that holds words, outermost first."""
    out, stack, i = [], [], 0
    # A flat pass: remember where each open tag's content began.
    for m in TAG.finditer(html):
        closing, tag, attrs, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if tag in VOID or selfclose:
            continue
        if not closing:
            stack.append((tag, m.end()))
        else:
            while stack:
                open_tag, content_start = stack.pop()
                if open_tag == tag:
                    out.append((open_tag, content_start, m.start()))
                    break
    return out


def extract(path: Path):
    html = path.read_text()
    units, claimed = [], []

    def is_free(a, b):
        return not any(s <= a and b <= e for s, e in claimed)

    for tag, a, b in sorted(spans(html), key=lambda s: (s[1], -s[2])):
        if tag in SKIP or tag not in LEAF:
            continue
        inner = html[a:b]
        if not inner.strip() or not re.search(r"[A-Za-zÀ-ÿ]", inner):
            continue
        # A leaf that holds a picture or another block is not a leaf.
        inside = {m.group(2).lower() for m in TAG.finditer(inner)}
        if inside - INLINE:
            continue
        if not is_free(a, b):
            continue
        claimed.append((a, b))
        units.append((a, b, inner.strip()))

    # The words that live in attributes rather than between tags.
    for m in TAG.finditer(html):
        tag, attrs = m.group(2).lower(), m.group(3)
        for am in re.finditer(r"\b([-a-zA-Z]+)\s*=\s*\"([^\"]*)\"", attrs):
            name, value = am.group(1).lower(), am.group(2)
            translatable = name in ATTRS or (
                tag == "meta" and re.search(r"name=\"(description)\"|property=\"og:(title|description)\"", attrs))
            if tag == "meta" and name != "content":
                translatable = False
            if not translatable or not value.strip() or not re.search(r"[A-Za-zÀ-ÿ]", value):
                continue
            s = m.start(3) + am.start(2)
            units.append((s, s + len(value), value))

    units.sort()
    template, out, last = [], {}, 0
    for a, b, text in units:
        template.append(html[last:a])
        template.append("{{" + text + "}}")
        out[text] = text
        last = b
    template.append(html[last:])
    return "".join(template), out


if __name__ == "__main__":
    src = Path(sys.argv[1])
    name = sys.argv[2]
    template, strings = extract(src)
    Path(f"templates/{name}.html").write_text(template)
    print(f"templates/{name}.html · {len(strings)} strings")
    Path(f"content/_{name}.json").write_text(
        json.dumps(strings, ensure_ascii=False, indent=2) + "\n")
