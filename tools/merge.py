"""Merge a batch of finished strings into a language, from stdin.

    python3 tools/merge.py fr < batch.json

Additive: a key already there is overwritten, everything else is left alone,
so a language can be translated in as many sittings as it takes.
"""
import json, sys
from pathlib import Path

code = sys.argv[1]
path = Path(f"content/{code}.json")
words = json.loads(path.read_text()) if path.exists() else {}
batch = json.loads(sys.stdin.read())

english = json.loads(Path("content/en.json").read_text())
unknown = [k for k in batch if k not in english]
if unknown:
    print("NOT IN THE SOURCE, refusing:", *[repr(k[:60]) for k in unknown], sep="\n  ")
    sys.exit(1)

words.update(batch)
# Kept in the English file's own order, so a diff between two languages lines up.
ordered = {k: words[k] for k in english if k in words}
path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n")
print(f"{code}: {len(ordered)} of {len(english)} translated")
