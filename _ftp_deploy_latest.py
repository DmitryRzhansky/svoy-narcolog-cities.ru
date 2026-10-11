# -*- coding: utf-8 -*-
import ftplib
import subprocess
import time
from pathlib import Path

HOST = "koroleld.beget.tech"
USER = "koroleld"
PASS = "Qetuosfhk12-//:"
REMOTE = "svoy-narcolog.ru/public_html"
LOCAL = Path(r"C:\svoy-narcolog-cities.ru")

# Files from latest commit
out = subprocess.check_output(
    ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
    cwd=LOCAL,
    text=True,
)
files = [
    line.strip().replace("\\", "/")
    for line in out.splitlines()
    if line.strip() and (LOCAL / line.strip()).is_file()
]
print("upload", len(files))
for f in files:
    print(" ", f)


def reconnect():
    for a in range(1, 10):
        try:
            ftp = ftplib.FTP(HOST, timeout=120)
            ftp.login(USER, PASS)
            ftp.encoding = "utf-8"
            ftp.set_pasv(True)
            print(f"connected attempt {a}")
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
n, errors = 0, []
for rel in files:
    rpath = f"{REMOTE}/{rel}"
    ensure_dir(ftp, "/".join(rpath.split("/")[:-1]))
    ok = False
    for attempt in range(1, 6):
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
