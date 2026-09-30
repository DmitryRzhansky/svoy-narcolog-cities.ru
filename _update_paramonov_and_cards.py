# -*- coding: utf-8 -*-
"""Replace Paramonov photo, fix doctor cards icons/alignment, prepare FTP list."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

ROOT = Path(r"C:\svoy-narcolog-cities.ru")
JPG = ROOT / "vrach-3.jpg"
PNG = Path(
    r"C:\Users\User\.cursor\projects\c-svoy-narcolog-cities-ru\assets"
    r"\c__Users_User_AppData_Roaming_Cursor_User_workspaceStorage_"
    r"b7882f4d92e22c2e43b44c507255be09_images_vrach-3-removebg-preview-"
    r"eada7d8e-5624-4b35-bc0b-481a511bb41c.png"
)

PROFILE_NAME = "paramonov-sergey-vladimirovich.webp"
PROFILE_OLD = "paramonov-sergey.webp"
ALT_FULL = "Парамонов Сергей Владимирович"
ALT_HERO = "Парамонов Сергей Владимирович, главный врач клиники"
ALT_PROFILE = "Парамонов Сергей Владимирович, главный врач, фельдшер-нарколог"

META_ICONS = {
    "Образование": "certificate",
    "Опыт работы": "clock",
    "Научная степень": "shield",
    "Квалификация": "check-circle",
    "Специализация": "target",
    "Дата рождения": "user",
    "Повышение квалификации": "lightbulb",
    "Профессиональные навыки": "check-circle",
    "Какие услуги оказывает": "aid",
}


def cutout_from_black(jpg: Path) -> Image.Image:
    rgb = Image.open(jpg).convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    alpha = Image.new("L", (w, h), 0)
    ap = alpha.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if r <= 22 and g <= 22 and b <= 22:
                ap[x, y] = 0
            elif r <= 40 and g <= 40 and b <= 40:
                ap[x, y] = min(255, int(((r + g + b) / 3 - 22) / 18 * 255))
            else:
                ap[x, y] = 255
    alpha = alpha.filter(ImageFilter.MedianFilter(size=3))
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.6))
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def refine_with_mask(base: Image.Image, mask_png: Path) -> Image.Image:
    if not mask_png.exists():
        return base
    m = Image.open(mask_png).convert("RGBA").resize(base.size, Image.Resampling.LANCZOS)
    ma = m.getchannel("A")
    ba = base.getchannel("A")
    combined = ImageChops.multiply(ba, ma.point(lambda v: 255 if v > 20 else 0))
    combined = combined.filter(ImageFilter.GaussianBlur(radius=0.4))
    out = base.copy()
    out.putalpha(combined)
    return out


def make_hero(img: Image.Image) -> Image.Image:
    bbox = img.getchannel("A").getbbox()
    img = img.crop(bbox)
    target_w, target_h = 694, 1120
    pad = 18
    max_w, max_h = target_w - pad * 2, target_h - pad * 2
    ratio = max_h / img.size[1]
    nw = max(1, int(img.size[0] * ratio))
    nh = max_h
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    if nw > max_w:
        left = (nw - max_w) // 2
        resized = resized.crop((left, 0, left + max_w, nh))
        nw = max_w
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    ox = (target_w - nw) // 2
    oy = target_h - pad - nh
    canvas.paste(resized, (ox, oy), resized)
    return canvas


def make_profile(img: Image.Image) -> Image.Image:
    bbox = img.getchannel("A").getbbox() or (0, 0, *img.size)
    img = img.crop(bbox)
    side = max(img.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ox = (side - img.size[0]) // 2
    oy = (side - img.size[1]) // 2
    canvas.paste(img, (ox, oy), img)
    out = canvas.resize((448, 448), Image.Resampling.LANCZOS)
    bg = Image.new("RGBA", (448, 448), (243, 250, 252, 255))
    bg.paste(out, (0, 0), out)
    return bg.convert("RGB")


def make_cta(img: Image.Image) -> Image.Image:
    bbox = img.getchannel("A").getbbox() or (0, 0, *img.size)
    img = img.crop(bbox)
    tw, th = 556, 525
    side_ratio = tw / th
    w, h = img.size
    if w / h > side_ratio:
        new_w = int(h * side_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / side_ratio)
        img = img.crop((0, 0, w, min(h, new_h)))
    out = img.resize((tw, th), Image.Resampling.LANCZOS)
    bg = Image.new("RGBA", (tw, th), (21, 72, 100, 255))
    bg.paste(out, (0, 0), out)
    return bg.convert("RGB")


def build_images() -> None:
    cutout = cutout_from_black(JPG)
    cutout = refine_with_mask(cutout, PNG)

    hero = make_hero(cutout)
    for dest in [
        ROOT / "assets/images/paramonov-glavnyy-vrach.webp",
        ROOT / "assets/images/doctor-paramonov.webp",
    ]:
        dest.parent.mkdir(parents=True, exist_ok=True)
        hero.save(dest, "WEBP", lossless=True, method=6)
        print("hero", dest.relative_to(ROOT), hero.size)

    profile = make_profile(cutout)
    profile_path = ROOT / "assets/images/doctors" / PROFILE_NAME
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile.save(profile_path, "WEBP", quality=92, method=6)
    print("profile", profile_path.relative_to(ROOT), profile.size)

    # Keep old filename as alias so nothing breaks mid-deploy
    alias = ROOT / "assets/images/doctors" / PROFILE_OLD
    profile.save(alias, "WEBP", quality=92, method=6)

    cta = make_cta(cutout)
    cta_path = ROOT / "assets/images/cta/paramonov.webp"
    cta.save(cta_path, "WEBP", quality=90, method=6)
    print("cta", cta_path.relative_to(ROOT), cta.size)


LABEL_PLAIN = re.compile(
    r'(<span class="doctor-profile__meta-label">)\s*'
    r"(Образование|Опыт работы|Научная степень|Квалификация|Специализация|"
    r"Дата рождения|Повышение квалификации|Профессиональные навыки|"
    r"Какие услуги оказывает)\s*(</span>)",
    re.I,
)


def inject_meta_icon(match: re.Match[str]) -> str:
    label = match.group(2)
    icon = META_ICONS.get(label, "info")
    return (
        f'{match.group(1)}\n'
        f'                      <span class="icon icon--{icon} doctor-profile__meta-icon" '
        f'aria-hidden="true"></span>\n'
        f"                      {label}\n"
        f"                    {match.group(3)}"
    )


def fix_alts_and_src(text: str) -> str:
    text = text.replace(f"doctors/{PROFILE_OLD}", f"doctors/{PROFILE_NAME}")

    # Hero / doctor-card alts
    text = re.sub(
        r'(src="[^"]*paramonov-glavnyy-vrach\.webp"\s*\n?\s*alt=")[^"]*(")',
        rf"\1{ALT_HERO}\2",
        text,
    )
    text = re.sub(
        r'(src="[^"]*doctor-paramonov\.webp"\s*\n?\s*alt=")[^"]*(")',
        rf"\1{ALT_HERO}\2",
        text,
    )
    text = re.sub(
        r'(src="[^"]*doctors/paramonov-sergey-vladimirovich\.webp"\s*\n?\s*alt=")[^"]*(")',
        rf"\1{ALT_PROFILE}\2",
        text,
    )
    text = re.sub(
        r'(src="[^"]*cta/paramonov\.webp"\s*\n?\s*alt=")[^"]*(")',
        rf"\1{ALT_FULL}, главный врач клиники\2",
        text,
    )
    # FAQ / consult that still mention Paramonov with old profile path already replaced
    text = re.sub(
        r'(alt=")Главный врач клиники Парамонов Сергей Владимирович[^"]*(")',
        rf"\1{ALT_PROFILE}\2",
        text,
    )
    text = re.sub(
        r'(alt=")Парамонов Сергей Владимирович, главный врач клиники(")',
        rf"\1{ALT_HERO}\2",
        text,
    )
    return text


def fix_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    text = fix_alts_and_src(text)
    text2, n = LABEL_PLAIN.subn(inject_meta_icon, text)
    if n:
        text = text2
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def fix_css() -> bool:
    css_path = ROOT / "assets/css/components/doctors.css"
    text = css_path.read_text(encoding="utf-8")
    original = text

    # Blue icons instead of red accent
    text = text.replace(
        ".doctor-profile__role-icon {\n"
        "  width: 0.8rem;\n"
        "  height: 0.8rem;\n"
        "  margin-top: 0.12rem;\n"
        "  color: var(--color-accent);\n"
        "}",
        ".doctor-profile__role-icon {\n"
        "  width: 0.8rem;\n"
        "  height: 0.8rem;\n"
        "  margin-top: 0.12rem;\n"
        "  color: var(--color-hero);\n"
        "}",
    )
    text = text.replace(
        ".doctor-profile__meta-icon {\n"
        "  width: 0.8rem;\n"
        "  height: 0.8rem;\n"
        "  color: var(--color-accent);\n"
        "}",
        ".doctor-profile__meta-icon {\n"
        "  width: 0.8rem;\n"
        "  height: 0.8rem;\n"
        "  color: var(--color-hero);\n"
        "}",
    )

    # Align meta values to content border under the text (not under icon)
    if "doctor-profile__meta-item {" in text and "align-items: start;" not in text.split(
        "doctor-profile__meta-item {"
    )[1][:120]:
        text = text.replace(
            ".doctor-profile__meta-item {\n  display: grid;\n  gap: 0.12rem;\n}",
            ".doctor-profile__meta-item {\n"
            "  display: grid;\n"
            "  gap: 0.12rem;\n"
            "  text-align: left;\n"
            "}",
        )

    text = text.replace(
        ".doctor-profile__meta-label {\n"
        "  display: grid;\n"
        "  grid-template-columns: 0.8rem minmax(0, 1fr);\n"
        "  column-gap: 0.4rem;\n"
        "  align-items: center;\n",
        ".doctor-profile__meta-label {\n"
        "  display: grid;\n"
        "  grid-template-columns: 0.95rem minmax(0, 1fr);\n"
        "  column-gap: 0.45rem;\n"
        "  align-items: center;\n"
        "  justify-items: start;\n",
    )
    text = text.replace(
        ".doctor-profile__meta-icon {\n"
        "  width: 0.8rem;\n"
        "  height: 0.8rem;\n"
        "  color: var(--color-hero);\n"
        "}",
        ".doctor-profile__meta-icon {\n"
        "  width: 0.95rem;\n"
        "  height: 0.95rem;\n"
        "  color: var(--color-hero);\n"
        "}",
    )
    text = text.replace(
        ".doctor-profile__meta-value {\n"
        "  padding-left: calc(0.8rem + 0.4rem);\n",
        ".doctor-profile__meta-value {\n"
        "  padding-left: calc(0.95rem + 0.45rem);\n"
        "  text-align: left;\n",
    )
    text = text.replace(
        ".doctor-profile__role {\n"
        "  display: grid;\n"
        "  grid-template-columns: 0.8rem minmax(0, 1fr);\n"
        "  gap: 0.4rem;\n"
        "  align-items: start;\n",
        ".doctor-profile__role {\n"
        "  display: grid;\n"
        "  grid-template-columns: 0.95rem minmax(0, 1fr);\n"
        "  gap: 0.45rem;\n"
        "  align-items: start;\n"
        "  justify-items: start;\n"
        "  text-align: left;\n",
    )
    text = text.replace(
        ".doctor-profile__role-icon {\n"
        "  width: 0.8rem;\n"
        "  height: 0.8rem;\n"
        "  margin-top: 0.12rem;\n"
        "  color: var(--color-hero);\n"
        "}",
        ".doctor-profile__role-icon {\n"
        "  width: 0.95rem;\n"
        "  height: 0.95rem;\n"
        "  margin-top: 0.15rem;\n"
        "  color: var(--color-hero);\n"
        "}",
    )

    if text != original:
        css_path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    build_images()
    css_changed = fix_css()
    print("css", css_changed)

    html_changed = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        if fix_html(path):
            html_changed += 1
            print("html", path.relative_to(ROOT))
    print("html_changed", html_changed)

    # sanity
    vrachi = (ROOT / "vrachi/index.html").read_text(encoding="utf-8")
    plain = len(re.findall(r'doctor-profile__meta-label">[А-Яа-я]', vrachi))
    with_icon = vrachi.count("doctor-profile__meta-icon")
    print("vrachi plain labels left", plain, "meta icons", with_icon)
    print("profile refs", vrachi.count(PROFILE_NAME), "old", vrachi.count(PROFILE_OLD))


if __name__ == "__main__":
    main()
