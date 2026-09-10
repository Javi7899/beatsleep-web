"""Change an English string without losing its translations.

    python3 tools/rekey.py "old English" "new English"

The key of a string is the English itself, which is what makes the content
files readable, and what makes editing the English a rename rather than an
edit. This does the rename in one move: the token in the templates and the
key in every language's content file, so no translation is orphaned and no
page falls back to English by accident.
"""
import json, sys
from pathlib import Path

old, new = sys.argv[1], sys.argv[2]
touched = []

for template in sorted(Path("templates").glob("*.html")):
    text = template.read_text()
    token = "{{" + old + "}}"
    if token in text:
        template.write_text(text.replace(token, "{{" + new + "}}"))
        touched.append(template.name)

for content in sorted(Path("content").glob("*.json")):
    if content.name.startswith("_"):
        continue
    words = json.loads(content.read_text())
    if old not in words:
        continue
    # English is its own translation, so it moves with the key.
    value = new if content.stem == "en" else words[old]
    rebuilt = {(new if k == old else k): (value if k == old else v)
               for k, v in words.items()}
    content.write_text(json.dumps(rebuilt, ensure_ascii=False, indent=2) + "\n")
    touched.append(content.name)

print(("renamed in " + ", ".join(touched)) if touched else f"not found: {old!r}")
