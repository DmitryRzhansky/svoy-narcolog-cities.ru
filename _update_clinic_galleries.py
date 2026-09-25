# -*- coding: utf-8 -*-
"""Update clinic photo galleries across HTML pages."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"C:\svoy-narcolog-cities.ru")
META = json.loads((ROOT / "_clinic_photos_meta.json").read_text(encoding="utf-8"))
BY_FILE = {m["file"]: m for m in META}

# Curated sets
HOME_FILES = [
    "dver-s-vyveskoy-svoy-narkolog.webp",
    "koridor-kliniki-golubye-steny.webp",
    "palata-statsionara-obshchiy-vid.webp",
    "palata-krovat-shtativ-shkafy.webp",
    "priem-pacienta-u-vracha.webp",
    "procedurnaya-s-medikamentami.webp",
]

SERVICE_FILES = HOME_FILES  # same strong set

GALLERY_ALL = [m["file"] for m in META]


def gallery_items(files: list[str], prefix: str, first_eager: bool = False) -> str:
    parts = []
    for i, name in enumerate(files):
        m = BY_FILE[name]
        alt = m["alt"]
        loading = (
            'fetchpriority="high"\n                decoding="async"'
            if first_eager and i == 0
            else 'loading="lazy"\n                decoding="async"'
        )
        parts.append(
            f"""          <li>
            <button
              class="gallery__item"
              type="button"
              data-lightbox-open
              data-lightbox-src="{prefix}assets/images/clinic/{name}"
              data-lightbox-alt="{alt}"
              data-lightbox-caption="{alt}"
              aria-label="Открыть фото: {alt}"
            >
              <img
                class="gallery__image"
                src="{prefix}assets/images/clinic/{name}"
                alt="{alt}"
                width="{m['w']}"
                height="{m['h']}"
                {loading}
              >
            </button>
          </li>"""
        )
    return "\n".join(parts)


def gallery_section(files: list[str], prefix: str, title_tag: str = "h2") -> str:
    items = gallery_items(files, prefix)
    return f"""      <section class="gallery" aria-labelledby="clinic-photos-title">
        <{title_tag} class="gallery__title" id="clinic-photos-title">
          Фотографии <span class="title-accent">нашей клиники</span>
        </{title_tag}>
        <ul class="gallery__grid">
{items}
        </ul>
      </section>
"""


def replace_ul_inside_gallery(html: str, files: list[str], prefix: str, first_eager: bool = False) -> str:
    """Replace first gallery__grid contents in a gallery section."""
    pattern = re.compile(
        r'(<section class="gallery[^"]*"[^>]*>[\s\S]*?<ul class="gallery__grid">)([\s\S]*?)(</ul>\s*</section>)',
        re.MULTILINE,
    )

    def repl(match: re.Match) -> str:
        return match.group(1) + "\n" + gallery_items(files, prefix, first_eager) + "\n        " + match.group(3)

    new_html, n = pattern.subn(repl, html, count=1)
    if n != 1:
        raise RuntimeError(f"gallery replace failed, matches={n}")
    return new_html


def update_about_alts(html: str) -> str:
    replacements = [
        (
            r'(src="(?:\.\./)*assets/images/about/lobby\.webp"\s+alt=")[^"]*("\s+width=")[^"]*("\s+height=")[^"]*',
            r'\1Светлый коридор клиники «Свой нарколог» с голубыми стенами\g<2>720\g<3>1280',
        ),
        (
            r'(src="(?:\.\./)*assets/images/about/doctor\.webp"\s+alt=")[^"]*("\s+width=")[^"]*("\s+height=")[^"]*',
            r'\1Приём пациента у врача в кабинете клиники\g<2>1280\g<3>960',
        ),
        (
            r'(src="(?:\.\./)*assets/images/about/ward\.webp"\s+alt=")[^"]*("\s+width=")[^"]*("\s+height=")[^"]*',
            r'\1Палата стационара клиники с кроватью и кушеткой\g<2>1280\g<3>960',
        ),
        (
            r'(src="(?:\.\./)*assets/images/about/drip\.webp"\s+alt=")[^"]*("\s+width=")[^"]*("\s+height=")[^"]*',
            r'\1Процедурный кабинет клиники с кушеткой и умывальником\g<2>1280\g<3>960',
        ),
        (
            r'(src="(?:\.\./)*assets/images/about/clinic-hall\.webp"\s+alt=")[^"]*("\s+width=")[^"]*("\s+height=")[^"]*',
            r'\1Кабинет приёма клиники с рабочим столом и креслами для посетителей\g<2>1280\g<3>960',
        ),
        (
            r'(src="(?:\.\./)*assets/images/about/clinic-night\.webp"\s+alt=")[^"]*("\s+width=")[^"]*("\s+height=")[^"]*',
            r'\1Вход в бизнес-центр, где расположена клиника «Свой нарколог»\g<2>720\g<3>1280',
        ),
    ]
    for pat, repl in replacements:
        html = re.sub(pat, repl, html)
    return html


def insert_gallery_after_guidelines(html: str, prefix: str) -> str:
    if 'id="clinic-photos-title"' in html:
        # already has clinic gallery — replace it
        return replace_ul_inside_gallery(html, SERVICE_FILES, prefix)

    # Insert after guidelines section (first occurrence of class="guidelines")
    # Find closing of that section carefully
    m = re.search(r'<section class="guidelines"[^>]*>', html)
    if not m:
        raise RuntimeError("guidelines section not found")

    start = m.start()
    # find matching close by scanning sections depth from start
    pos = m.end()
    depth = 1
    while depth and pos < len(html):
        next_open = html.find("<section", pos)
        next_close = html.find("</section>", pos)
        if next_close == -1:
            raise RuntimeError("unclosed guidelines")
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 8
        else:
            depth -= 1
            pos = next_close + len("</section>")

    insert_at = pos
    block = "\n" + gallery_section(SERVICE_FILES, prefix)
    return html[:insert_at] + block + html[insert_at:]


def depth_prefix(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return ""
    depth = rel.count("/")
    return "../" * depth


updated = []

# Homepage
index = ROOT / "index.html"
html = index.read_text(encoding="utf-8")
html = replace_ul_inside_gallery(html, HOME_FILES, "")
html = update_about_alts(html)
index.write_text(html, encoding="utf-8", newline="\n")
updated.append("index.html")

# Fotogalereya
foto = ROOT / "fotogalereya" / "index.html"
html = foto.read_text(encoding="utf-8")
html = replace_ul_inside_gallery(html, GALLERY_ALL, "../", first_eager=True)
foto.write_text(html, encoding="utf-8", newline="\n")
updated.append("fotogalereya/index.html")

# o-nas
onas = ROOT / "o-nas" / "index.html"
html = onas.read_text(encoding="utf-8")
html = update_about_alts(html)
onas.write_text(html, encoding="utf-8", newline="\n")
updated.append("o-nas/index.html")

# Service pages with guidelines
service_pages = []
for p in (ROOT / "uslugi").rglob("index.html"):
    text = p.read_text(encoding="utf-8")
    if 'class="guidelines"' in text:
        service_pages.append(p)

for p in service_pages:
    prefix = depth_prefix(p)
    html = p.read_text(encoding="utf-8")
    html = insert_gallery_after_guidelines(html, prefix)
    p.write_text(html, encoding="utf-8", newline="\n")
    updated.append(p.relative_to(ROOT).as_posix())

print(f"Updated {len(updated)} files")
for u in updated:
    print(" -", u)
