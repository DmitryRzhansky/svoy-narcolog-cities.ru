from pathlib import Path
import re
from PIL import Image

idx = Path("index.html").read_text(encoding="utf-8")
vr = Path("vrachi/index.html").read_text(encoding="utf-8")
print("index beskova", "beskova" in idx.lower())
print("vrachi beskova", "beskova" in vr.lower())
print("index roles", len(re.findall("doctor-profile__role", idx)))
print("vrachi roles", len(re.findall("doctor-profile__role", vr)))
print("index all-card", "doctor-profile--all" in idx)
print("glasses", "doctor-glasses.webp" in idx)
print("old cta", "cta/paramonov.webp" in idx)
m = re.search(r'<ul class="doctors__grid">([\s\S]*?)</ul>', idx)
names = re.findall("doctor-profile__name\">([^<]+)", m.group(1))
print("names", names)
print("all btn", "Смотреть всех" in m.group(1))
b = sum(1 for p in Path(".").rglob("index.html") if "vrachi" not in p.parts and "beskova-anastasiya" in p.read_text(encoding="utf-8"))
c = sum(1 for p in Path(".").rglob("index.html") if "cta/paramonov.webp" in p.read_text(encoding="utf-8"))
print("non-vrachi beskova", b, "old cta pages", c)
im = Image.open("assets/images/paramonov-glavnyy-vrach.webp").convert("RGBA")
print("hero bbox", im.getchannel("A").getbbox())
# compare carve vs removebg
carve = Path(r"C:\Users\User\.cursor\projects\c-svoy-narcolog-cities-ru\assets\c__Users_User_AppData_Roaming_Cursor_User_workspaceStorage_b7882f4d92e22c2e43b44c507255be09_images_vrach-3-no-bg-preview__carve.photos_-ed11a925-5b0d-41a9-b25e-a0716685ef38.png")
rim = Image.open(carve).convert("RGBA")
print("carve", rim.size, rim.getchannel("A").getbbox(), "a0", sum(1 for v in rim.getchannel("A").getdata() if v==0))
