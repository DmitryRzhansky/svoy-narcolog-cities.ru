# -*- coding: utf-8 -*-
"""Remove old Metrika 112969766, add call_click goal before </body>, FTP upload."""
from __future__ import annotations

import ftplib
import re
import time
from pathlib import Path

ROOT = Path(r"C:\svoy-narcolog-cities.ru")

HOST = "koroleld.beget.tech"
USER = "koroleld"
PASS = "Qetuosfhk12-//:"
REMOTE = "svoy-narcolog.ru/public_html"

OLD_ID = "112969766"
NEW_ID = "113058828"

# Remove whole old counter block (comments + script + noscript)
OLD_BLOCK = re.compile(
    r"\s*<!--\s*Yandex\.Metrika counter\s*-->\s*"
    r"<script\b[\s\S]*?"
    rf"tag\.js\?id={OLD_ID}[\s\S]*?"
    r"</script>\s*"
    rf"<noscript>[\s\S]*?watch/{OLD_ID}[\s\S]*?</noscript>\s*"
    r"<!--\s*/Yandex\.Metrika counter\s*-->",
    re.I,
)

# Fallback: strip remaining old-id leftovers
OLD_LEFTOVERS = re.compile(
    rf".*{OLD_ID}.*\n?",
)

CALL_SNIPPET = """    <script>
document.addEventListener('click', function (e) {
  var a = e.target.closest('a[href^="tel:"]');
  if (a) ym(113058828, 'reachGoal', 'call_click');
});
</script>
"""

changed: list[str] = []

for path in ROOT.rglob("*.html"):
    if ".git" in path.parts:
        continue
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    orig = text

    text2, n = OLD_BLOCK.subn("\n", text, count=1)
    text = text2

    # Safety: remove any remaining lines with old counter id
    if OLD_ID in text:
        text = "\n".join(
            line for line in text.splitlines(keepends=True) if OLD_ID not in line
        )

    if "reachGoal', 'call_click'" not in text and 'reachGoal", "call_click"' not in text:
        if "</body>" in text:
            text = text.replace("</body>", CALL_SNIPPET + "  </body>", 1)
        else:
            print("NO BODY", rel)

    if text != orig:
        # normalize: avoid triple blank lines from block removal
        text = re.sub(r"\n{3,}", "\n\n", text)
        path.write_text(text, encoding="utf-8", newline="\n")
        changed.append(rel)
        print("ok", rel)
    else:
        print("unchanged", rel)

print("TOTAL", len(changed))

# Sanity
idx = (ROOT / "index.html").read_text(encoding="utf-8")
assert OLD_ID not in idx, "old counter still in index"
assert NEW_ID in idx, "new counter missing"
assert "call_click" in idx, "call_click missing"
assert idx.count("Yandex.Metrika counter") == 2  # open + close of one block
print("sanity ok")


def reconnect():
    for a in range(1, 10):
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
    rpath = f"{REMOTE}/{rel}"
    ensure_dir(ftp, "/".join(rpath.split("/")[:-1]))
    ok = False
    for attempt in range(1, 6):
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
