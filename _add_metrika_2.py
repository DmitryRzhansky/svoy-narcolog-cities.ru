# -*- coding: utf-8 -*-
import ftplib
import time
from pathlib import Path

ROOT = Path(r"C:\svoy-narcolog-cities.ru")

HOST = "koroleld.beget.tech"
USER = "koroleld"
PASS = "Qetuosfhk12-//:"
REMOTE = "svoy-narcolog.ru/public_html"

COUNTER_ID = "113058828"
ANCHOR = "<!-- /Yandex.Metrika counter -->"
SNIPPET = f"""
    <!-- Yandex.Metrika counter -->
    <script type="text/javascript">
      (function(m,e,t,r,i,k,a){{
        m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
      }})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id={COUNTER_ID}', 'ym');

      ym({COUNTER_ID}, 'init', {{ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true}});
    </script>
    <noscript><div><img src="https://mc.yandex.ru/watch/{COUNTER_ID}" style="position:absolute; left:-9999px;" alt=""></div></noscript>
    <!-- /Yandex.Metrika counter -->"""

changed = []
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts:
        continue
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    if f"tag.js?id={COUNTER_ID}" in text:
        print("skip", rel)
        continue
    if ANCHOR in text:
        new = text.replace(ANCHOR, ANCHOR + SNIPPET, 1)
    elif "</head>" in text:
        new = text.replace("</head>", SNIPPET.lstrip("\n") + "\n  </head>", 1)
    else:
        print("NO ANCHOR", rel)
        continue
    path.write_text(new, encoding="utf-8", newline="\n")
    changed.append(rel)
    print("ok", rel)

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


ftp = reconnect()
n, errors = 0, []
for rel in changed:
    rpath = f"{REMOTE}/{rel}"
    ok = False
    for attempt in range(1, 5):
        try:
            with open(ROOT / rel, "rb") as f:
                ftp.storbinary(f"STOR {rpath}", f, blocksize=64 * 1024)
            n += 1
            ok = True
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
