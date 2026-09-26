import ftplib
import time
from pathlib import Path

HOST = "koroleld.beget.tech"
USER = "koroleld"
PASS = "Qetuosfhk12-//:"
REMOTE = "svoy-narcolog.ru/public_html"
LOCAL = Path(r"C:\svoy-narcolog-cities.ru")

files = [
    "assets/css/components/doctors.css",
    "assets/images/paramonov-glavnyy-vrach.webp",
    "assets/images/cta/paramonov.webp",
    "assets/images/doctors/paramonov-sergey.webp",
    "assets/images/doctor-paramonov.webp",
    "vrachi/index.html",
    "index.html",
]
for p in (LOCAL / "uslugi").rglob("index.html"):
    files.append(p.relative_to(LOCAL).as_posix())

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
    for attempt in range(1, 5):
        try:
            with open(LOCAL / rel, "rb") as f:
                ftp.storbinary(f"STOR {rpath}", f, blocksize=64 * 1024)
            n += 1
            if n % 15 == 0:
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
    else:
        errors.append(rel)

try:
    ftp.quit()
except Exception:
    pass
print("DONE", n, "errors", len(errors))
for e in errors:
    print("ERR", e)
