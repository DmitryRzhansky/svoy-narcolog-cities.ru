# -*- coding: utf-8 -*-
from pathlib import Path
import re
import ftplib
import time

ROOT = Path(r"C:\svoy-narcolog-cities.ru")
TAG = (
    '<meta name="google-site-verification" '
    'content="aCqbwEOm7s7u3tb_JInM-P9Cx8lxqGPysd2LHeRcYpE">'
)
TOKEN = "aCqbwEOm7s7u3tb_JInM-P9Cx8lxqGPysd2LHeRcYpE"
EXISTING = "yCi9iWCC5wzStGNC5Ev62zSTNNNmQkoJSesGzlP1YvE"

HOST = "koroleld.beget.tech"
USER = "koroleld"
PASS = "Qetuosfhk12-//:"
REMOTE = "svoy-narcolog.ru/public_html"

changed = []
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    if TOKEN in text:
        print("skip", path.relative_to(ROOT))
        continue

    if EXISTING in text:
        new = re.sub(
            rf'(<meta name="google-site-verification" content="{re.escape(EXISTING)}"[^>]*>)',
            rf"\1\n    {TAG}",
            text,
            count=1,
        )
    elif 'name="yandex-verification"' in text:
        new = re.sub(
            r'(<meta name="yandex-verification" content="[^"]*"[^>]*>)',
            rf"\1\n    {TAG}",
            text,
            count=1,
        )
    elif 'name="viewport"' in text:
        new = re.sub(
            r'(<meta name="viewport"[^>]*>)',
            rf"\1\n    {TAG}",
            text,
            count=1,
        )
    else:
        print("NO ANCHOR", path.relative_to(ROOT))
        continue

    if new == text:
        print("FAILED", path.relative_to(ROOT))
        continue

    path.write_text(new, encoding="utf-8", newline="\n")
    changed.append(path.relative_to(ROOT).as_posix())
    print("ok", path.relative_to(ROOT))

print("TOTAL", len(changed))


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
n, errors = 0, []
for rel in changed:
    rpath = f"{REMOTE}/{rel}".replace("\\", "/")
    ensure_dir(ftp, "/".join(rpath.split("/")[:-1]))
    ok = False
    for attempt in range(1, 5):
        try:
            with open(ROOT / rel, "rb") as f:
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

assert TOKEN in (ROOT / "index.html").read_text(encoding="utf-8")
print("index ok")
