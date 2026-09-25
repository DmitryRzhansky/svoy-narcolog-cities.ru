import ftplib
import time
from pathlib import Path

HOST = "koroleld.beget.tech"
USER = "koroleld"
PASS = "Qetuosfhk12-//:"
REMOTE = "svoy-narcolog.ru/public_html"
LOCAL = Path(r"C:\svoy-narcolog-cities.ru")

files = [
    "assets/css/components/about.css",
    "index.html",
    "assets/images/about/lobby.webp",
    "assets/images/about/doctor.webp",
    "assets/images/about/ward.webp",
    "assets/images/about/drip.webp",
    "fotogalereya/index.html",
]

for p in (LOCAL / "uslugi").rglob("index.html"):
    text = p.read_text(encoding="utf-8")
    if "dver-s-vyveskoy-svoy-narkolog.webp" in text:
        files.append(p.relative_to(LOCAL).as_posix())


def reconnect():
    for a in range(1, 8):
        try:
            ftp = ftplib.FTP(HOST, timeout=120)
            ftp.login(USER, PASS)
            ftp.encoding = "utf-8"
            ftp.set_pasv(True)
            return ftp
        except Exception as e:
            print("connect fail", a, e)
            time.sleep(2 * a)
    raise RuntimeError("no ftp")


ftp = reconnect()
uploaded = 0
for rel in files:
    rpath = f"{REMOTE}/{rel}"
    for attempt in range(1, 5):
        try:
            with open(LOCAL / rel, "rb") as f:
                ftp.storbinary(f"STOR {rpath}", f, blocksize=64 * 1024)
            uploaded += 1
            print("ok", rel)
            break
        except Exception as e:
            print("retry", attempt, rel, e)
            try:
                ftp.quit()
            except Exception:
                pass
            time.sleep(1.5 * attempt)
            ftp = reconnect()

try:
    ftp.quit()
except Exception:
    pass
print("DONE", uploaded)
