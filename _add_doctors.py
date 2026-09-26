# -*- coding: utf-8 -*-
"""Prepare new doctor images and patch HTML across the site."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\svoy-narcolog-cities.ru")
DOCTORS = ROOT / "assets" / "images" / "doctors"
CTA = ROOT / "assets" / "images" / "cta"
ASSETS = ROOT / "assets" / "images"


def save_webp(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "WEBP", quality=90, method=6)
    print(f"saved {path.relative_to(ROOT)} {img.size}")


def square_crop(img: Image.Image, size: int = 448) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    # Bias slightly upward to keep face in frame for portraits
    left = (w - side) // 2
    top = max(0, int((h - side) * 0.12))
    if top + side > h:
        top = h - side
    crop = img.crop((left, top, left + side, top + side))
    return crop.resize((size, size), Image.Resampling.LANCZOS)


def hero_portrait(img: Image.Image, width: int = 694, height: int = 1120) -> Image.Image:
    target_ratio = width / height
    w, h = img.size
    src_ratio = w / h
    if src_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        crop = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = max(0, int((h - new_h) * 0.08))
        if top + new_h > h:
            top = h - new_h
        crop = img.crop((0, top, w, top + new_h))
    return crop.resize((width, height), Image.Resampling.LANCZOS)


def cta_crop(img: Image.Image, width: int = 556, height: int = 525) -> Image.Image:
    target_ratio = width / height
    w, h = img.size
    src_ratio = w / h
    if src_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        crop = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = max(0, int((h - new_h) * 0.05))
        if top + new_h > h:
            top = h - new_h
        crop = img.crop((0, top, w, top + new_h))
    return crop.resize((width, height), Image.Resampling.LANCZOS)


# --- images ---
src1 = Image.open(ROOT / "vrach-1.jpg")
src2 = Image.open(ROOT / "vrach-2.jpg")
src3 = Image.open(ROOT / "vrach-3.jpg")

save_webp(square_crop(src1), DOCTORS / "morozov-ruslan.webp")
save_webp(square_crop(src2), DOCTORS / "beskova-anastasiya.webp")
save_webp(square_crop(src3), DOCTORS / "paramonov-sergey.webp")
save_webp(hero_portrait(src3), ASSETS / "doctor-paramonov.webp")
save_webp(cta_crop(src3), CTA / "paramonov.webp")

# Card HTML snippets (relative prefix injected later)
BESKOVA_CARD = """          <li>
            <article class="doctor-profile">
              <figure class="doctor-profile__media">
                <img
                  class="doctor-profile__image"
                  src="{prefix}assets/images/doctors/beskova-anastasiya.webp"
                  alt="Бескова Анастасия Дмитриевна, врач психиатр-нарколог"
                  width="448"
                  height="448"
                  loading="lazy"
                  decoding="async"
                >
              </figure>
              <div class="doctor-profile__body">
                <span class="doctor-profile__name">Бескова Анастасия Дмитриевна</span>
                <p class="doctor-profile__role">
                  <span class="icon icon--stethoscope doctor-profile__role-icon" aria-hidden="true"></span>
                  <span>Психиатр-нарколог, психиатр</span>
                </p>
                <ul class="doctor-profile__meta">
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Образование</span>
                    <span class="doctor-profile__meta-value">ИвГМА, лечебное дело; ординатура психиатрия-наркология (ИвГМУ)</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Опыт работы</span>
                    <span class="doctor-profile__meta-value">6&nbsp;лет</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Специализация</span>
                    <span class="doctor-profile__meta-value">Детоксикация, купирование абстиненции, кодирование</span>
                  </li>
                </ul>
              </div>
            </article>
          </li>
"""

MOROZOV_CARD = """          <li>
            <article class="doctor-profile">
              <figure class="doctor-profile__media">
                <img
                  class="doctor-profile__image"
                  src="{prefix}assets/images/doctors/morozov-ruslan.webp"
                  alt="Морозов Руслан Антонович, специалист по наркологии"
                  width="448"
                  height="448"
                  loading="lazy"
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
                    <span class="doctor-profile__meta-label">Образование</span>
                    <span class="doctor-profile__meta-value">Среднее профессиональное (медицинское)</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Опыт работы</span>
                    <span class="doctor-profile__meta-value">с&nbsp;2022&nbsp;года</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Специализация</span>
                    <span class="doctor-profile__meta-value">Инфузионная терапия, купирование абстиненции</span>
                  </li>
                </ul>
              </div>
            </article>
          </li>
"""

PARAMONOV_CARD_PAGE = """          <li>
            <article class="doctor-profile">
              <figure class="doctor-profile__media">
                <img
                  class="doctor-profile__image"
                  src="../assets/images/doctors/paramonov-sergey.webp"
                  alt="Парамонов Сергей Владимирович, главный врач, фельдшер-нарколог"
                  width="448"
                  height="448"
                  loading="lazy"
                  decoding="async"
                >
              </figure>
              <div class="doctor-profile__body">
                <span class="doctor-profile__name">Парамонов Сергей Владимирович</span>
                <p class="doctor-profile__role">
                  <span class="icon icon--stethoscope doctor-profile__role-icon" aria-hidden="true"></span>
                  <span>Главный врач, фельдшер-нарколог</span>
                </p>
                <p class="doctor-profile__bio">
                  Руководит выездной помощью: детоксикация, купирование абстиненции и острых состояний на дому.
                </p>
                <ul class="doctor-profile__meta">
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Образование</span>
                    <span class="doctor-profile__meta-value">Среднее профессиональное (лечебное дело)</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Опыт работы</span>
                    <span class="doctor-profile__meta-value">14&nbsp;лет</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Специализация</span>
                    <span class="doctor-profile__meta-value">Наркология и психиатрия, неотложная помощь</span>
                  </li>
                </ul>
              </div>
            </article>
          </li>
"""

BESKOVA_CARD_PAGE = """          <li>
            <article class="doctor-profile">
              <figure class="doctor-profile__media">
                <img
                  class="doctor-profile__image"
                  src="../assets/images/doctors/beskova-anastasiya.webp"
                  alt="Бескова Анастасия Дмитриевна, врач психиатр-нарколог"
                  width="448"
                  height="448"
                  loading="lazy"
                  decoding="async"
                >
              </figure>
              <div class="doctor-profile__body">
                <span class="doctor-profile__name">Бескова Анастасия Дмитриевна</span>
                <p class="doctor-profile__role">
                  <span class="icon icon--stethoscope doctor-profile__role-icon" aria-hidden="true"></span>
                  <span>Психиатр-нарколог, психиатр</span>
                </p>
                <p class="doctor-profile__bio">
                  Проводит детоксикацию, купирует абстиненцию и металкогольные психозы, подбирает терапию и кодирование.
                </p>
                <ul class="doctor-profile__meta">
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Образование</span>
                    <span class="doctor-profile__meta-value">ИвГМА, лечебное дело (2023); ординатура психиатрия-наркология, ИвГМУ (2026)</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Опыт работы</span>
                    <span class="doctor-profile__meta-value">6&nbsp;лет, из них 2 по специальности «психиатр-нарколог»</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Специализация</span>
                    <span class="doctor-profile__meta-value">Экстренная наркологическая помощь и противорецидивная терапия</span>
                  </li>
                </ul>
              </div>
            </article>
          </li>
"""

MOROZOV_CARD_PAGE = """          <li>
            <article class="doctor-profile">
              <figure class="doctor-profile__media">
                <img
                  class="doctor-profile__image"
                  src="../assets/images/doctors/morozov-ruslan.webp"
                  alt="Морозов Руслан Антонович, специалист по наркологии"
                  width="448"
                  height="448"
                  loading="lazy"
                  decoding="async"
                >
              </figure>
              <div class="doctor-profile__body">
                <span class="doctor-profile__name">Морозов Руслан Антонович</span>
                <p class="doctor-profile__role">
                  <span class="icon icon--aid doctor-profile__role-icon" aria-hidden="true"></span>
                  <span>Наркология</span>
                </p>
                <p class="doctor-profile__bio">
                  Проводит инфузионную терапию, контролирует витальные показатели и купирует тяжёлую абстиненцию.
                </p>
                <ul class="doctor-profile__meta">
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Образование</span>
                    <span class="doctor-profile__meta-value">Среднее профессиональное (медицинское)</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Опыт работы</span>
                    <span class="doctor-profile__meta-value">с&nbsp;2022&nbsp;года</span>
                  </li>
                  <li class="doctor-profile__meta-item">
                    <span class="doctor-profile__meta-label">Специализация</span>
                    <span class="doctor-profile__meta-value">Вывод из запоя, кодирование, детоксикация</span>
                  </li>
                </ul>
              </div>
            </article>
          </li>
"""


def depth_prefix(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return ""
    return "../" * rel.count("/")


def patch_hero(html: str, prefix: str) -> str:
    if "doctor-golev.webp" not in html and "hero__person" not in html:
        return html

    html = html.replace(
        f'{prefix}assets/images/doctor-golev.webp',
        f'{prefix}assets/images/doctor-paramonov.webp',
    )
    # Hero person block name/role/exp (common pattern)
    html = re.sub(
        r'(class="hero__photo"\s+src="[^"]+doctor-paramonov\.webp"\s+alt=")[^"]*"',
        r'\1Парамонов Сергей Владимирович, главный врач, фельдшер-нарколог"',
        html,
        count=1,
    )
    html = re.sub(
        r'(<article class="doctor-card">[\s\S]*?<span class="doctor-card__name">)[^<]+(</span>)',
        r'\1Парамонов Сергей Владимирович\2',
        html,
        count=1,
    )
    # Replace first two doctor-card lines after name in hero
    html = re.sub(
        r'(<span class="doctor-card__name">Парамонов Сергей Владимирович</span>\s*'
        r'<p class="doctor-card__line">\s*'
        r'<span class="icon icon--caret doctor-card__mark"[^>]*></span>\s*)[^<]+(\s*</p>\s*'
        r'<p class="doctor-card__line">\s*'
        r'<span class="icon icon--caret doctor-card__mark"[^>]*></span>\s*)[^<]+',
        r'\1Главный врач, фельдшер-нарколог\2Стаж работы: 14 лет',
        html,
        count=1,
    )
    return html


def patch_consult(html: str) -> str:
    html = html.replace(
        "assets/images/cta/doctor-glasses.webp",
        "assets/images/cta/paramonov.webp",
    )
    html = re.sub(
        r'(src="[^"]*assets/images/cta/paramonov\.webp"\s+alt=")[^"]*"',
        r'\1Парамонов Сергей Владимирович, главный врач клиники"',
        html,
    )
    return html


def patch_faq_authors(html: str, prefix: str) -> str:
    # Replace any FAQ author photo + name + role blocks with Paramonov
    pattern = re.compile(
        r'(<div class="faq-item__author">\s*'
        r'<img\s+class="faq-item__photo"\s+src=")[^"]+("\s+alt=""\s+width="104"\s+height="104"[\s\S]*?'
        r'<p class="faq-item__author-name">)[^<]+(</p>\s*'
        r'<p class="faq-item__author-role">)[^<]+(</p>)',
        re.MULTILINE,
    )

    def repl(m: re.Match) -> str:
        return (
            m.group(1)
            + f"{prefix}assets/images/doctors/paramonov-sergey.webp"
            + m.group(2)
            + "Парамонов Сергей Владимирович"
            + m.group(3)
            + "главный врач, фельдшер-нарколог"
            + m.group(4)
        )

    return pattern.sub(repl, html)


def insert_doctors_cards(html: str, prefix: str) -> str:
    if "beskova-anastasiya.webp" in html:
        return html
    marker = '<article class="doctor-profile doctor-profile--all">'
    idx = html.find(marker)
    if idx == -1:
        return html
    # Find the <li> that starts this article
    li_start = html.rfind("<li>", 0, idx)
    if li_start == -1:
        return html
    insert = BESKOVA_CARD.format(prefix=prefix) + MOROZOV_CARD.format(prefix=prefix)
    return html[:li_start] + insert + html[li_start:]


def patch_vrachi_page(html: str) -> str:
    if "paramonov-sergey.webp" in html and "beskova-anastasiya.webp" in html:
        return html
    # Insert after first doctor (Golev) card's closing </li>
    # Find first doctor-profile (not --all) and insert new cards near the top after Golev
    marker = "Голев Сергей Михайлович"
    pos = html.find(marker)
    if pos == -1:
        return html
    # find end of this </li> after the article
    li_end = html.find("</li>", pos)
    if li_end == -1:
        return html
    li_end += len("</li>")
    insert = "\n" + PARAMONOV_CARD_PAGE + BESKOVA_CARD_PAGE + MOROZOV_CARD_PAGE
    return html[:li_end] + insert + html[li_end:]


updated = []
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    original = text
    prefix = depth_prefix(path)
    rel = path.relative_to(ROOT).as_posix()

    text = patch_consult(text)
    text = patch_faq_authors(text, prefix)

    if 'class="hero__person"' in text or "doctor-golev.webp" in text:
        text = patch_hero(text, prefix)

    if 'section class="doctors"' in text and "doctor-profile--all" in text:
        text = insert_doctors_cards(text, prefix)

    if rel == "vrachi/index.html":
        text = patch_vrachi_page(text)

    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        updated.append(rel)

print(f"Updated {len(updated)} HTML files")
for u in updated:
    print(" -", u)
