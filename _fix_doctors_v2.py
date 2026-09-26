# -*- coding: utf-8 -*-
"""Fix doctors page, cross-page block, full bios, hero no-bg photo."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\svoy-narcolog-cities.ru")
SRC_NO_BG = ROOT / "_paramonov-no-bg.png"


def make_hero_transparent(src: Path, dest: Path) -> tuple[int, int]:
    img = Image.open(src).convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            # Treat near-black as background (cutout on black)
            if r <= 18 and g <= 18 and b <= 18:
                pixels[x, y] = (0, 0, 0, 0)
    # Fit to hero-ish portrait size
    target_w, target_h = 694, 1120
    ratio = min(target_w / w, target_h / h)
    nw, nh = max(1, int(w * ratio)), max(1, int(h * ratio))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    ox = (target_w - nw) // 2
    oy = target_h - nh  # bottom-align like current hero
    canvas.paste(resized, (ox, oy), resized)
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, "WEBP", lossless=True, method=6)
    print(f"hero saved {dest.name} {canvas.size}")
    return canvas.size


# Also update CTA crop from no-bg (on transparent / keep upper body)
def make_cta(src: Path, dest: Path) -> None:
    img = Image.open(src).convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r <= 18 and g <= 18 and b <= 18:
                pixels[x, y] = (0, 0, 0, 0)
    # Crop upper body roughly
    tw, th = 556, 525
    # Use content bounding box
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    w, h = img.size
    # Prefer top portion
    side_ratio = tw / th
    if w / h > side_ratio:
        new_w = int(h * side_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / side_ratio)
        img = img.crop((0, 0, w, min(h, new_h)))
    out = img.resize((tw, th), Image.Resampling.LANCZOS)
    # Composite on soft clinic-like teal for CTA card that expects opaque photo
    bg = Image.new("RGBA", (tw, th), (21, 72, 100, 255))
    bg.paste(out, (0, 0), out)
    bg.convert("RGB").save(dest, "WEBP", quality=90, method=6)
    print(f"cta saved {dest.name}")


# Square profile from no-bg for doctors folder paramonov
def make_profile(src: Path, dest: Path) -> None:
    img = Image.open(src).convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r <= 18 and g <= 18 and b <= 18:
                pixels[x, y] = (0, 0, 0, 0)
    bbox = img.getbbox() or (0, 0, w, h)
    img = img.crop(bbox)
    # square on light surface bg matching cards
    side = max(img.size)
    canvas = Image.new("RGBA", (side, side), (255, 255, 255, 0))
    ox = (side - img.size[0]) // 2
    oy = (side - img.size[1]) // 2
    canvas.paste(img, (ox, oy), img)
    out = canvas.resize((448, 448), Image.Resampling.LANCZOS)
    bg = Image.new("RGBA", (448, 448), (243, 250, 252, 255))  # #f3fafc
    bg.paste(out, (0, 0), out)
    bg.convert("RGB").save(dest, "WEBP", quality=90, method=6)
    print(f"profile saved {dest.name}")


hero_path = ROOT / "assets" / "images" / "paramonov-glavnyy-vrach.webp"
cta_path = ROOT / "assets" / "images" / "cta" / "paramonov.webp"
profile_path = ROOT / "assets" / "images" / "doctors" / "paramonov-sergey.webp"
old_hero = ROOT / "assets" / "images" / "doctor-paramonov.webp"

make_hero_transparent(SRC_NO_BG, hero_path)
make_cta(SRC_NO_BG, cta_path)
make_profile(SRC_NO_BG, profile_path)

# Keep alias for any remaining refs during replace
if old_hero.exists():
    # overwrite old file with new so broken refs still work temporarily
    Image.open(hero_path).save(old_hero, "WEBP", lossless=True, method=6)

# --- Full detailed cards ---
PARAMONOV_FULL = """          <li>
            <article class="doctor-profile doctor-profile--full">
              <figure class="doctor-profile__media">
                <img
                  class="doctor-profile__image"
                  src="{prefix}assets/images/doctors/paramonov-sergey.webp"
                  alt="Главный врач клиники Парамонов Сергей Владимирович, фельдшер-нарколог"
                  width="448"
                  height="448"
                  {loading}
                  decoding="async"
                >
              </figure>
              <div class="doctor-profile__body">
                <span class="doctor-profile__name">Парамонов Сергей Владимирович</span>
                <p class="doctor-profile__role">
                  <span class="icon icon--stethoscope doctor-profile__role-icon" aria-hidden="true"></span>
                  <span>Главный врач, фельдшер СМП, фельдшер-нарколог</span>
                </p>
                <ul class="doctor-profile__meta">
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--certificate doctor-profile__meta-icon" aria-hidden="true"></span>
                      Образование
                    </span>
                    <span class="doctor-profile__meta-value">Среднее профессиональное (лечебное дело)</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--target doctor-profile__meta-icon" aria-hidden="true"></span>
                      Специализация
                    </span>
                    <span class="doctor-profile__meta-value">Фельдшер СМП, фельдшер-нарколог</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--lightbulb doctor-profile__meta-icon" aria-hidden="true"></span>
                      Повышение квалификации
                    </span>
                    <span class="doctor-profile__meta-value">Нет</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--clock doctor-profile__meta-icon" aria-hidden="true"></span>
                      Опыт работы
                    </span>
                    <span class="doctor-profile__meta-value">14&nbsp;лет (с&nbsp;2012&nbsp;года) в наркологии и психиатрии</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--check-circle doctor-profile__meta-icon" aria-hidden="true"></span>
                      Профессиональные навыки
                    </span>
                    <span class="doctor-profile__meta-value">Сбор жалоб и анамнеза, оценка физического и психического статуса пациента, инструментальная диагностика, купирование острых состояний, подбор медикаментозной терапии</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--aid doctor-profile__meta-icon" aria-hidden="true"></span>
                      Какие услуги оказывает
                    </span>
                    <span class="doctor-profile__meta-value">Оказание экстренной и неотложной помощи: купирование абстинентного синдрома, детоксикационная терапия, лечение острых интоксикаций, купирование металкогольных психозов на догоспитальном этапе, запретительные процедуры, мотивационное консультирование</span>
                  </li>
                </ul>
              </div>
            </article>
          </li>
"""

BESKOVA_FULL = """          <li>
            <article class="doctor-profile doctor-profile--full">
              <figure class="doctor-profile__media">
                <img
                  class="doctor-profile__image"
                  src="{prefix}assets/images/doctors/beskova-anastasiya.webp"
                  alt="Врач психиатр-нарколог Бескова Анастасия Дмитриевна"
                  width="448"
                  height="448"
                  {loading}
                  decoding="async"
                >
              </figure>
              <div class="doctor-profile__body">
                <span class="doctor-profile__name">Бескова Анастасия Дмитриевна</span>
                <p class="doctor-profile__role">
                  <span class="icon icon--stethoscope doctor-profile__role-icon" aria-hidden="true"></span>
                  <span>Врач психиатр-нарколог, психиатр</span>
                </p>
                <ul class="doctor-profile__meta">
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--user doctor-profile__meta-icon" aria-hidden="true"></span>
                      Дата рождения
                    </span>
                    <span class="doctor-profile__meta-value">16&nbsp;августа&nbsp;1999&nbsp;г.</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--certificate doctor-profile__meta-icon" aria-hidden="true"></span>
                      Образование
                    </span>
                    <span class="doctor-profile__meta-value">Высшее, специалитет — лечебное дело (ИвГМА, 2023&nbsp;г.); ординатура — психиатрия-наркология (ИвГМУ, 2026&nbsp;г.); первичная переподготовка — психиатрия (ИвГМУ, 2026&nbsp;г.)</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--target doctor-profile__meta-icon" aria-hidden="true"></span>
                      Специализация
                    </span>
                    <span class="doctor-profile__meta-value">Врач психиатр-нарколог, психиатр</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--lightbulb doctor-profile__meta-icon" aria-hidden="true"></span>
                      Повышение квалификации
                    </span>
                    <span class="doctor-profile__meta-value">Нет</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--clock doctor-profile__meta-icon" aria-hidden="true"></span>
                      Опыт работы
                    </span>
                    <span class="doctor-profile__meta-value">6&nbsp;лет, из них 2 по специальности «психиатр-нарколог»</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--check-circle doctor-profile__meta-icon" aria-hidden="true"></span>
                      Профессиональные навыки
                    </span>
                    <span class="doctor-profile__meta-value">Сбор жалоб и анамнеза, оценка физического и психического статуса пациента, инструментальная диагностика, купирование острых состояний, подбор медикаментозной терапии, психотерапевтическая помощь, профилактика рецидивов</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--aid doctor-profile__meta-icon" aria-hidden="true"></span>
                      Какие услуги оказывает
                    </span>
                    <span class="doctor-profile__meta-value">Оказание экстренной и неотложной помощи: купирование абстинентного синдрома, детоксикационная терапия, лечение острых интоксикаций, купирование металкогольных психозов на догоспитальном этапе, запретительные процедуры, мотивационное консультирование</span>
                  </li>
                </ul>
              </div>
            </article>
          </li>
"""

MOROZOV_FULL = """          <li>
            <article class="doctor-profile doctor-profile--full">
              <figure class="doctor-profile__media">
                <img
                  class="doctor-profile__image"
                  src="{prefix}assets/images/doctors/morozov-ruslan.webp"
                  alt="Специалист по наркологии Морозов Руслан Антонович"
                  width="448"
                  height="448"
                  {loading}
                  decoding="async"
                >
              </figure>
              <div class="doctor-profile__body">
                <span class="doctor-profile__name">Морозов Руслан Антонович</span>
                <p class="doctor-profile__role">
                  <span class="icon icon--aid doctor-profile__role-icon" aria-hidden="true"></span>
                  <span>Наркология</span>
                </p>
                <ul class="doctor-profile__meta">
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--user doctor-profile__meta-icon" aria-hidden="true"></span>
                      Дата рождения
                    </span>
                    <span class="doctor-profile__meta-value">21.05.2002</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--target doctor-profile__meta-icon" aria-hidden="true"></span>
                      Специализация
                    </span>
                    <span class="doctor-profile__meta-value">Наркология</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--certificate doctor-profile__meta-icon" aria-hidden="true"></span>
                      Образование
                    </span>
                    <span class="doctor-profile__meta-value">Среднее профессиональное (медицинское)</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--lightbulb doctor-profile__meta-icon" aria-hidden="true"></span>
                      Повышение квалификации
                    </span>
                    <span class="doctor-profile__meta-value">Регулярное прохождение курсов усовершенствования кадров, изучение современных методов дезинтоксикационной терапии и оказания неотложной наркологической помощи</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--clock doctor-profile__meta-icon" aria-hidden="true"></span>
                      Опыт работы
                    </span>
                    <span class="doctor-profile__meta-value">С&nbsp;2022&nbsp;года</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--check-circle doctor-profile__meta-icon" aria-hidden="true"></span>
                      Профессиональные навыки
                    </span>
                    <span class="doctor-profile__meta-value">Проведение инфузионной терапии любой сложности, контроль витальных показателей (АД, пульс, сатурация, ЭКГ, глюкометрия), экстренное купирование тяжёлых состояний и абстиненции</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">
                      <span class="icon icon--aid doctor-profile__meta-icon" aria-hidden="true"></span>
                      Какие услуги оказывает
                    </span>
                    <span class="doctor-profile__meta-value">Безопасное выведение из запоя (на дому и амбулаторно); купирование алкогольного абстинентного синдрома; медикаментозное кодирование и противорецидивная терапия; снятие похмельного синдрома и общая детоксикация организма</span>
                  </li>
                </ul>
              </div>
            </article>
          </li>
"""

CROSS_PAGE_GRID = """        <ul class="doctors__grid">
{paramonov}
{beskova}
{morozov}
          <li>
            <article class="doctor-profile doctor-profile--all">
              <figure class="doctor-profile__all-media">
                <img
                  class="doctor-profile__all-image"
                  src="{prefix}assets/images/doctors/all-doctors.webp"
                  alt=""
                  width="900"
                  height="1200"
                  loading="lazy"
                  decoding="async"
                >
              </figure>
              <a
                class="button button--hero doctor-profile__all-cta"
                href="/vrachi/"
              >
                <span>Смотреть всех</span>
                <span class="button__arrow">
                  <span class="icon icon--arrow" aria-hidden="true"></span>
                </span>
              </a>
            </article>
          </li>
        </ul>
"""


def depth_prefix(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return ""
    return "../" * rel.count("/")


def fix_vrachi_page(html: str) -> str:
    # Remove wrongly inserted doctor cards from site-meta
    html = re.sub(
        r'(<ul class="site-meta">\s*'
        r'<li class="site-meta__item">[\s\S]*?</li>)\s*'
        r'(?:<li>\s*<article class="doctor-profile">[\s\S]*?</article>\s*</li>\s*)+'
        r'(<li class="site-meta__item">)',
        r"\1\n\n      \2",
        html,
        count=1,
    )

    # Remove any remaining new-doctor cards that were wrongly duplicated in the main grid
    # (we'll re-insert cleanly at the start of the grid)
    for name in (
        "paramonov-sergey.webp",
        "beskova-anastasiya.webp",
        "morozov-ruslan.webp",
    ):
        html = re.sub(
            rf'\s*<li>\s*<article class="doctor-profile(?: doctor-profile--full)?">[\s\S]*?{re.escape(name)}[\s\S]*?</article>\s*</li>',
            "",
            html,
        )

    cards = (
        PARAMONOV_FULL.format(prefix="../", loading='fetchpriority="high"')
        + BESKOVA_FULL.format(prefix="../", loading='loading="lazy"')
        + MOROZOV_FULL.format(prefix="../", loading='loading="lazy"')
    )

    # Insert after <ul class="doctors__grid">
    html = re.sub(
        r'(<ul class="doctors__grid">\s*)',
        r"\1" + cards,
        html,
        count=1,
    )
    return html


def replace_cross_page_doctors(html: str, prefix: str) -> str:
    if 'section class="doctors"' not in html or "doctor-profile--all" not in html:
        return html
    if 'doctors--page' in html:
        return html

    grid = CROSS_PAGE_GRID.format(
        prefix=prefix,
        paramonov=PARAMONOV_FULL.format(prefix=prefix, loading='loading="lazy"'),
        beskova=BESKOVA_FULL.format(prefix=prefix, loading='loading="lazy"'),
        morozov=MOROZOV_FULL.format(prefix=prefix, loading='loading="lazy"'),
    )

    html = re.sub(
        r'<ul class="doctors__grid">[\s\S]*?</ul>\s*(?=</section>)',
        grid + "\n      ",
        html,
        count=1,
    )
    return html


def patch_hero_refs(html: str) -> str:
    html = html.replace(
        "assets/images/doctor-paramonov.webp",
        "assets/images/paramonov-glavnyy-vrach.webp",
    )
    html = re.sub(
        r'(src="[^"]*paramonov-glavnyy-vrach\.webp"\s+alt=")[^"]*"',
        r'\1Главный врач клиники Парамонов Сергей Владимирович"',
        html,
    )
    return html


updated = []
vrachi = ROOT / "vrachi" / "index.html"
text = vrachi.read_text(encoding="utf-8")
new = fix_vrachi_page(text)
new = patch_hero_refs(new)
if new != text:
    vrachi.write_text(new, encoding="utf-8", newline="\n")
    updated.append("vrachi/index.html")

for path in ROOT.rglob("*.html"):
    if ".git" in path.parts:
        continue
    rel = path.relative_to(ROOT).as_posix()
    if rel == "vrachi/index.html":
        continue
    text = path.read_text(encoding="utf-8")
    prefix = depth_prefix(path)
    new = replace_cross_page_doctors(text, prefix)
    new = patch_hero_refs(new)
    if new != text:
        path.write_text(new, encoding="utf-8", newline="\n")
        updated.append(rel)

print(f"Updated {len(updated)} files")
for u in updated:
    print(" -", u)

# sanity: site-meta should not contain doctor-profile
vm = (ROOT / "vrachi" / "index.html").read_text(encoding="utf-8")
if 'site-meta' in vm:
    chunk = vm[vm.find('site-meta'): vm.find('</ul>', vm.find('site-meta')) + 5]
    if "doctor-profile" in chunk:
        print("WARNING: doctor-profile still inside site-meta")
    else:
        print("OK: site-meta clean")
print("paramonov cards on vrachi:", vm.count("paramonov-sergey.webp"))
print("beskova on vrachi:", vm.count("beskova-anastasiya.webp"))
print("golev on index:", "Голев Сергей Михайлович" in (ROOT / "index.html").read_text(encoding="utf-8") and 'id="doctors"' in (ROOT/"index.html").read_text(encoding="utf-8"))
idx = (ROOT / "index.html").read_text(encoding="utf-8")
# check doctors section specifically
m = re.search(r'<section class="doctors"[^>]*>[\s\S]*?</section>', idx)
if m:
    sec = m.group(0)
    print("index doctors has Golev:", "Голев" in sec)
    print("index doctors has Beskova:", "Бескова" in sec)
    print("index doctors has Paramonov:", "Парамонов" in sec)
    print("index hero file:", "paramonov-glavnyy-vrach.webp" in idx)
