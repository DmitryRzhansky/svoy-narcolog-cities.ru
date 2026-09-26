# -*- coding: utf-8 -*-
"""Fix doctors teaser UI, hero cutout framing, restore consult photo."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(r"C:\svoy-narcolog-cities.ru")
SRC = Path(
    r"C:\Users\User\.cursor\projects\c-svoy-narcolog-cities-ru\assets"
    r"\c__Users_User_AppData_Roaming_Cursor_User_workspaceStorage_"
    r"b7882f4d92e22c2e43b44c507255be09_images_vrach-3-removebg-preview-"
    r"814c4a6c-b3fc-4869-824c-033d78ee590b.png"
)
HERO_OUT = ROOT / "assets" / "images" / "paramonov-glavnyy-vrach.webp"
HERO_COPY = ROOT / "assets" / "images" / "doctor-paramonov.webp"


def clean_cutout(img: Image.Image) -> Image.Image:
    """Drop leftover near-black fringe around a transparent cutout."""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            # Near-black leftovers from remove.bg preview
            if r <= 28 and g <= 28 and b <= 28 and a < 250:
                px[x, y] = (0, 0, 0, 0)
                continue
            if r <= 18 and g <= 18 and b <= 18:
                px[x, y] = (0, 0, 0, 0)
    # Soften jagged alpha edges slightly
    alpha = img.getchannel("A").filter(ImageFilter.MedianFilter(size=3))
    img.putalpha(alpha)
    return img


def make_hero(src: Path, *dests: Path) -> None:
    img = clean_cutout(Image.open(src))
    bbox = img.getchannel("A").getbbox()
    if not bbox:
        raise RuntimeError("empty alpha bbox")
    img = img.crop(bbox)

    target_w, target_h = 694, 1120
    # Match Golev framing: fill almost the full canvas (~2.5% pad)
    pad = 20
    max_w, max_h = target_w - pad * 2, target_h - pad * 2
    ratio = min(max_w / img.size[0], max_h / img.size[1])
    nw = max(1, int(img.size[0] * ratio))
    nh = max(1, int(img.size[1] * ratio))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    ox = (target_w - nw) // 2
    # Bottom-align like Golev hero photo
    oy = target_h - pad - nh
    if oy < pad:
        oy = pad
    canvas.paste(resized, (ox, oy), resized)

    for dest in dests:
        dest.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(dest, "WEBP", lossless=True, method=6)
        print(f"hero -> {dest.relative_to(ROOT)} {canvas.size} content={(ox, oy, ox + nw, oy + nh)}")


BESKOVA_LI = re.compile(
    r"\s*<li>\s*"
    r'<article class="doctor-profile doctor-profile--full">\s*'
    r'<figure class="doctor-profile__media">\s*'
    r'<img[^>]*beskova-anastasiya\.webp[\s\S]*?</article>\s*</li>',
    re.I,
)

ROLE_BLOCK = re.compile(
    r"\s*<p class=\"doctor-profile__role\">[\s\S]*?</p>",
    re.I,
)


def is_vrachi_page(path: Path) -> bool:
    return path.as_posix().replace("\\", "/").endswith("/vrachi/index.html") or path.name == "vrachi"


def fix_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    # Restore consult photo everywhere
    text = text.replace("cta/paramonov.webp", "cta/doctor-glasses.webp")

    if not is_vrachi_page(path) and "doctors__grid" in text:
        text2, n = BESKOVA_LI.subn("", text)
        if n:
            text = text2
        # Remove role lines under names in teaser cards
        # Limit to doctors section to avoid unrelated matches
        def strip_roles_in_doctors(m: re.Match[str]) -> str:
            block = m.group(0)
            block = ROLE_BLOCK.sub("", block)
            return block

        text = re.sub(
            r'(<ul class="doctors__grid">[\s\S]*?</ul>)',
            strip_roles_in_doctors,
            text,
            count=1,
        )
        # Safety net: remove any leftover role lines outside /vrachi/
        text = ROLE_BLOCK.sub("", text)

    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    if not SRC.exists():
        # Fallback to local copy
        alt = ROOT / "_paramonov-nobg2.png"
        src = alt if alt.exists() else SRC
    else:
        src = SRC
    print("source", src)
    make_hero(src, HERO_OUT, HERO_COPY)

    changed = []
    for path in ROOT.rglob("index.html"):
        if "node_modules" in path.parts:
            continue
        if fix_html(path):
            changed.append(path.relative_to(ROOT).as_posix())
    print(f"html updated: {len(changed)}")
    for p in changed[:40]:
        print(" ", p)


if __name__ == "__main__":
    main()
