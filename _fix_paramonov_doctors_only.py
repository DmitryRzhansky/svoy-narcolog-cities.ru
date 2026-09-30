# -*- coding: utf-8 -*-
"""Replace Paramonov photo only in doctors block / vrachi page."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\svoy-narcolog-cities.ru")
SRC = Path(
    r"C:\Users\User\.cursor\projects\c-svoy-narcolog-cities-ru\assets"
    r"\c__Users_User_AppData_Roaming_Cursor_User_workspaceStorage_"
    r"b7882f4d92e22c2e43b44c507255be09_images_vrach-3-464cfc69-ce93-43a9-ab90-9affcb728580.jpg"
)

NAME = "paramonov-sergey-vladimirovich.webp"
HERO_FALLBACK = "paramonov-glavnyy-vrach.webp"
ALT = "Парамонов Сергей Владимирович"
OUT = ROOT / "assets/images/doctors" / NAME


def save_webp() -> tuple[int, int]:
    img = Image.open(SRC).convert("RGB")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "WEBP", quality=90, method=6)
    print("saved", OUT.relative_to(ROOT), img.size)
    return img.size


def patch_doctors_section(section: str, w: int, h: int) -> str:
    """Update Paramonov profile img inside a doctors section only."""

    def fix_img(m: re.Match[str]) -> str:
        block = m.group(0)
        # force named file
        block = re.sub(
            r'src="([^"]*?/)(?:paramonov-glavnyy-vrach|doctor-paramonov|paramonov-sergey(?:-vladimirovich)?)\.webp"',
            rf'src="\1{NAME}"',
            block,
        )
        block = re.sub(
            r'src="(?:paramonov-glavnyy-vrach|doctor-paramonov|paramonov-sergey(?:-vladimirovich)?)\.webp"',
            f'src="{NAME}"',
            block,
        )
        block = re.sub(r'alt="[^"]*"', f'alt="{ALT}"', block)
        block = re.sub(r'width="\d+"', f'width="{w}"', block)
        block = re.sub(r'height="\d+"', f'height="{h}"', block)
        return block

    # only doctor-profile images of Paramonov in this section
    return re.sub(
        r'<img\b(?:(?!>).)*?(?:paramonov-sergey(?:-vladimirovich)?|paramonov-glavnyy-vrach|doctor-paramonov)\.webp(?:(?!>).)*?>',
        fix_img,
        section,
        flags=re.I | re.S,
    )


def revert_outside_doctors(text: str) -> str:
    """Hero / FAQ / etc. must not use the new doctors filename."""

    def revert_img(m: re.Match[str]) -> str:
        block = m.group(0)
        block = block.replace(
            f"doctors/{NAME}",
            HERO_FALLBACK,
        )
        # if somehow path is just the name under images/
        block = re.sub(
            rf'src="([^"]*/){re.escape(NAME)}"',
            rf'src="\1{HERO_FALLBACK}"',
            block,
        )
        return block

    parts = re.split(
        r'(<section\b[^>]*\bclass="[^"]*\bdoctors\b[^"]*"[^>]*>[\s\S]*?</section>)',
        text,
        flags=re.I,
    )
    out = []
    for i, part in enumerate(parts):
        is_doctors = bool(
            re.match(
                r'<section\b[^>]*\bclass="[^"]*\bdoctors\b',
                part,
                flags=re.I,
            )
        )
        if is_doctors:
            out.append(part)
            continue
        out.append(
            re.sub(
                rf'<img\b(?:(?!>).)*?{re.escape(NAME)}(?:(?!>).)*?>',
                revert_img,
                part,
                flags=re.I | re.S,
            )
        )
    return "".join(out)


def fix_html(path: Path, w: int, h: int) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text

    def fix_section(m: re.Match[str]) -> str:
        return patch_doctors_section(m.group(0), w, h)

    text = re.sub(
        r'<section\b[^>]*\bclass="[^"]*\bdoctors\b[^"]*"[^>]*>[\s\S]*?</section>',
        fix_section,
        text,
        flags=re.I,
    )

    text = revert_outside_doctors(text)

    if text != orig:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    w, h = save_webp()
    n = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        if fix_html(path, w, h):
            n += 1
            print("html", path.relative_to(ROOT))
    print("html_changed", n)

    # sanity
    idx = (ROOT / "index.html").read_text(encoding="utf-8")
    hero = re.search(
        r'class="hero__photo"[\s\S]*?src="([^"]+)"',
        idx,
    )
    docs = re.search(
        r'<section\b[^>]*\bdoctors\b[^>]*>[\s\S]*?paramonov[^"]+\.webp',
        idx,
        re.I,
    )
    print("hero src", hero.group(1) if hero else None)
    print(
        "doctors has named file",
        NAME in (docs.group(0) if docs else ""),
    )
    vrachi = (ROOT / "vrachi/index.html").read_text(encoding="utf-8")
    print("vrachi named", NAME in vrachi)
    assert "hero__photo" in idx
    assert HERO_FALLBACK in hero.group(1)
    assert NAME in vrachi


if __name__ == "__main__":
    main()
