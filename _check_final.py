from pathlib import Path
import re
ROOT = Path(".")
# final checks
idx = (ROOT/"index.html").read_text(encoding="utf-8")
assert "beskova-anastasiya" not in idx
assert "doctor-glasses.webp" in idx
assert "cta/paramonov.webp" not in idx
sec = re.search(r'<section class="doctors\b[\s\S]*?</section>', idx).group(0)
assert "doctor-profile--all" in sec
assert "Смотреть всех" in sec
assert "morozov-ruslan" in sec
assert "paramonov-sergey" in sec
assert 'class="doctor-profile__role"' not in sec
vr = (ROOT/"vrachi/index.html").read_text(encoding="utf-8")
assert "beskova-anastasiya" in vr
# non-vrachi must not have roles in doctors section
bad = []
for p in ROOT.rglob("index.html"):
    if "vrachi" in p.parts: continue
    t = p.read_text(encoding="utf-8")
    m = re.search(r'<section class="doctors\b[\s\S]*?</section>', t)
    if not m: continue
    if 'class="doctor-profile__role"' in m.group(0):
        bad.append(str(p))
    if "beskova-anastasiya" in m.group(0):
        bad.append("beskova:"+str(p))
print("bad", bad)
print("ok")
