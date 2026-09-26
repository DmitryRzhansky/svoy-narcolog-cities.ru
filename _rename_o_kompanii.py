from pathlib import Path

ROOT = Path(r"C:\svoy-narcolog-cities.ru")
changed = []

for p in list(ROOT.rglob("*.html")) + list(ROOT.rglob("*.xml")):
    if ".git" in p.parts:
        continue
    text = p.read_text(encoding="utf-8")
    new = text.replace("О компании", "О клинике")
    new = new.replace('title-accent">компании</span>', 'title-accent">клинике</span>')
    if new != text:
        p.write_text(new, encoding="utf-8", newline="\n")
        changed.append(p.relative_to(ROOT).as_posix())

print("files", len(changed))
for f in changed:
    print(f)

left = []
for p in ROOT.rglob("*.html"):
    if ".git" in p.parts:
        continue
    t = p.read_text(encoding="utf-8")
    if "О компании" in t or 'title-accent">компании</span>' in t:
        left.append(p.relative_to(ROOT).as_posix())
print("leftover", left)
