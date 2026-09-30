# -*- coding: utf-8 -*-
import ftplib
import time
from pathlib import Path

HOST = "koroleld.beget.tech"
USER = "koroleld"
PASS = "Qetuosfhk12-//:"
REMOTE = "svoy-narcolog.ru/public_html"
LOCAL = Path(r"C:\svoy-narcolog-cities.ru")

files = [
    "assets/images/doctors/paramonov-sergey-vladimirovich.webp",
    "assets/images/doctors/paramonov-sergey.webp",
    "assets/images/paramonov-glavnyy-vrach.webp",
    "assets/images/doctor-paramonov.webp",
    "assets/images/cta/paramonov.webp",
]
for p in LOCAL.rglob("*.html"):
    if ".git" in p.parts:
        continue
    t = p.read_text(encoding="utf-8")
    if "paramonov-sergey-vladimirovich" in t:
        files.append(p.relative_to(LOCAL).as_posix())

seen = set()
uniq = []
for f in files:
    if f not in seen:
        seen.add(f)
        uniq.append(f)
files = uniq
print("upload", len(files))


def reconnect():
    for a in range(1, 8):
        try:
            ftp = ftplib.FTP(HOST, timeout=120)
            ftp.login(USER, PASS)
            ftp.encoding = "utf-8"
            ftp.set_pasv(True)
            return ftp
        except Exception as e:
            print("fail", a, e)
            time.sleep(2 * a)
    raise RuntimeError("no ftp")


def ensure_dir(ftp, remote_dir: str):
    parts = remote_dir.replace("\\", "/").strip("/").split("/")
    path = ""
    for part in parts:
        path = f"{path}/{part}" if path else part
        try:
            ftp.mkd(path)
        except Exception:
            pass


ftp = reconnect()
n = 0
errors = []
for rel in files:
    rpath = f"{REMOTE}/{rel}".replace("\\", "/")
    parent = "/".join(rpath.split("/")[:-1])
    ensure_dir(ftp, parent)
    ok = False
    for attempt in range(1, 5):
        try:
            with open(LOCAL / rel, "rb") as f:
                ftp.storbinary(f"STOR {rpath}", f, blocksize=64 * 1024)
            n += 1
            ok = True
            if n % 10 == 0:
                print("...", n)
            break
        except Exception as e:
            print("retry", attempt, rel, e)
            try:
                ftp.quit()
            except Exception:
                pass
            time.sleep(1.5 * attempt)
            ftp = reconnect()
    if not ok:
        errors.append(rel)

try:
    ftp.quit()
except Exception:
    pass
print("DONE", n, "errors", len(errors))
for e in errors:
    print("ERR", e)
