# -*- coding: utf-8 -*-
from pathlib import Path
import re
from PIL import Image, ImageFilter, ImageChops

ROOT = Path(r"C:\svoy-narcolog-cities.ru")
JPG = Path(r"C:\Users\User\.cursor\projects\c-svoy-narcolog-cities-ru\assets\c__svoy-narcolog-cities.ru_vrach-3.jpg")
PNG = Path(r"C:\Users\User\.cursor\projects\c-svoy-narcolog-cities-ru\assets\c__Users_User_AppData_Roaming_Cursor_User_workspaceStorage_b7882f4d92e22c2e43b44c507255be09_images_vrach-3-removebg-preview-814c4a6c-b3fc-4869-824c-033d78ee590b.png")


def cutout_from_black(jpg: Path) -> Image.Image:
    """Key black studio background from original JPG, soften edges."""
    rgb = Image.open(jpg).convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    alpha = Image.new("L", (w, h), 0)
    ap = alpha.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            # luminance / near-black
            if r <= 22 and g <= 22 and b <= 22:
                ap[x, y] = 0
            elif r <= 40 and g <= 40 and b <= 40:
                # soft fringe
                ap[x, y] = min(255, int(((r + g + b) / 3 - 22) / 18 * 255))
            else:
                ap[x, y] = 255
    # Clean speckles
    alpha = alpha.filter(ImageFilter.MedianFilter(size=3))
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.6))
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def refine_with_mask(base: Image.Image, mask_png: Path) -> Image.Image:
    """Intersect with removebg mask if available for safer hair edges."""
    if not mask_png.exists():
        return base
    m = Image.open(mask_png).convert("RGBA").resize(base.size, Image.Resampling.LANCZOS)
    ma = m.getchannel("A")
    # Keep pixel if either our key OR strong removebg says subject
    # Prefer intersection near edges: use max of both alphas lightly
    ba = base.getchannel("A")
    # Use removebg as guide: if removebg is 0, force transparent
    combined = ImageChops.multiply(ba, ma.point(lambda v: 255 if v > 20 else 0))
    # Soften
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


img = cutout_from_black(JPG)
img = refine_with_mask(img, PNG)
canvas = make_hero(img)
for dest in [
    ROOT / "assets/images/paramonov-glavnyy-vrach.webp",
    ROOT / "assets/images/doctor-paramonov.webp",
]:
    canvas.save(dest, "WEBP", lossless=True, method=6)
    print("saved", dest.name, canvas.getchannel("A").getbbox())

ROLE = re.compile(r"\s*<p class=\"doctor-profile__role\">[\s\S]*?</p>", re.I)
changed = 0
for path in ROOT.rglob("index.html"):
    if "vrachi" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    if "doctors__grid" not in text:
        continue
    # Strip roles only inside doctors section
    def fix_section(m):
        return ROLE.sub("", m.group(0))

    new = re.sub(
        r'(<section class="doctors\b[\s\S]*?</section>)',
        fix_section,
        text,
        count=1,
    )
    if new != text:
        path.write_text(new, encoding="utf-8", newline="\n")
        changed += 1
print("role-stripped pages", changed)

# quick check index
idx = (ROOT / "index.html").read_text(encoding="utf-8")
sec = re.search(r'<section class="doctors\b[\s\S]*?</section>', idx).group(0)
print("roles left in doctors", len(re.findall("doctor-profile__role\"", sec)))
print("names", re.findall(r'doctor-profile__name">([^<]+)', sec))
print("has all", "doctor-profile--all" in sec)
