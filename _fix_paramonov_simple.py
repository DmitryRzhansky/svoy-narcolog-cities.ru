# -*- coding: utf-8 -*-
from pathlib import Path
import re

ROOT = Path(r"C:\svoy-narcolog-cities.ru")
ALT = "Парамонов Сергей Владимирович"
NAME = "paramonov-sergey-vladimirovich.webp"
W, H = 433, 577

# One <img> tag only: no '>' between <img and closing >
IMG_RE = re.compile(
    rf'<img\b(?:(?!>).)*?src="[^"]*{re.escape(NAME)}"(?:(?!>).)*?>',
    re.I | re.S,
)


def fix_img(block: str) -> str:
    block = re.sub(r'width="\d+"', f'width="{W}"', block)
    block = re.sub(r'height="\d+"', f'height="{H}"', block)
    block = re.sub(r'alt="[^"]*"', f'alt="{ALT}"', block)
    return block


changed = 0
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    orig = text

    text = text.replace(
        "assets/images/paramonov-glavnyy-vrach.webp",
        f"assets/images/doctors/{NAME}",
    )
    text = text.replace(
        "assets/images/doctor-paramonov.webp",
        f"assets/images/doctors/{NAME}",
    )
    text = text.replace(
        "assets/images/doctors/paramonov-sergey.webp",
        f"assets/images/doctors/{NAME}",
    )

    text = IMG_RE.sub(lambda m: fix_img(m.group(0)), text)

    if text != orig:
        path.write_text(text, encoding="utf-8", newline="\n")
        changed += 1
        print(path.relative_to(ROOT))

print("changed", changed)

# sanity: icons must stay intact
idx = (ROOT / "index.html").read_text(encoding="utf-8")
assert 'map-pin.svg" alt="" width="20"' in idx or 'map-pin.svg" alt="" width="20" height="20"' in idx
assert idx.count(NAME) >= 1
assert 'star.svg" alt="Парамонов' not in idx
print("sanity ok, refs", idx.count(NAME))
