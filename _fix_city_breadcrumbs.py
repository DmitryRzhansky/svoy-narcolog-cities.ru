# -*- coding: utf-8 -*-
"""Breadcrumbs: Главная -> Услуги -> Город (не ссылка) -> Услуга."""
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

CITIES = {
    "shuya": "Шуя",
    "kineshma": "Кинешма",
    "kokhma": "Кохма",
    "furmanov": "Фурманов",
    "privolzhsk": "Приволжск",
}

SERVICES = {
    "vyzov-narkologa": "Вызов нарколога на дом",
    "kapelnitsa-ot-zapoya": "Капельница от запоя",
    "vyvod-iz-zapoya": "Вывод из запоя",
    "kodirovanie-ot-alkogolya": "Кодирование от алкоголя",
}

NAV_RE = re.compile(
    r'<nav class="hero__breadcrumbs"[^>]*>[\s\S]*?</nav>',
    re.I,
)

BREADCRUMB_JSON_RE = re.compile(
    r'(\{\s*"@type"\s*:\s*"BreadcrumbList"[\s\S]*?"itemListElement"\s*:\s*)\[[\s\S]*?\](\s*\})',
    re.I,
)


def html_crumbs(city: str, service: str) -> str:
    return f"""            <nav class="hero__breadcrumbs" aria-label="Хлебные крошки">
              <ol class="hero__breadcrumbs-list">
                <li class="hero__breadcrumbs-item">
                  <a class="hero__breadcrumbs-link" href="/">Главная</a>
                </li>
                <li class="hero__breadcrumbs-item">
                  <a class="hero__breadcrumbs-link" href="/uslugi/">Услуги</a>
                </li>
                <li class="hero__breadcrumbs-item">
                  <span class="hero__breadcrumbs-city">{city}</span>
                </li>
                <li class="hero__breadcrumbs-item">
                  <span class="hero__breadcrumbs-current">{service}</span>
                </li>
              </ol>
            </nav>"""


def json_crumbs(city: str, service: str, page_url: str) -> str:
    # City has no "item" — not a link
    return f"""[
        {{
          "@type": "ListItem",
          "position": 1,
          "name": "Главная",
          "item": "https://svoy-narcolog.ru/"
        }},
        {{
          "@type": "ListItem",
          "position": 2,
          "name": "Услуги",
          "item": "https://svoy-narcolog.ru/uslugi/"
        }},
        {{
          "@type": "ListItem",
          "position": 3,
          "name": "{city}"
        }},
        {{
          "@type": "ListItem",
          "position": 4,
          "name": "{service}",
          "item": "{page_url}"
        }}
      ]"""


def fix_file(path: Path, city: str, service: str, page_url: str) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text

    if not NAV_RE.search(text):
        print("NO NAV", path.relative_to(ROOT))
        return False

    text = NAV_RE.sub(html_crumbs(city, service), text, count=1)

    def repl_json(m: re.Match[str]) -> str:
        return m.group(1) + json_crumbs(city, service, page_url) + m.group(2)

    text2, n = BREADCRUMB_JSON_RE.subn(repl_json, text, count=1)
    if n:
        text = text2
    else:
        print("NO JSON", path.relative_to(ROOT))

    if text == orig:
        return False
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


changed: list[str] = []

# City subpages
for service_slug, service_name in SERVICES.items():
    for city_slug, city_name in CITIES.items():
        path = ROOT / "uslugi" / service_slug / city_slug / "index.html"
        if not path.exists():
            print("MISSING", path.relative_to(ROOT))
            continue
        url = f"https://svoy-narcolog.ru/uslugi/{service_slug}/{city_slug}/"
        if fix_file(path, city_name, service_name, url):
            changed.append(path.relative_to(ROOT).as_posix())
            print("ok", path.relative_to(ROOT))

# Ivanovo hubs (service roots)
for service_slug, service_name in SERVICES.items():
    path = ROOT / "uslugi" / service_slug / "index.html"
    if not path.exists():
        print("MISSING", path.relative_to(ROOT))
        continue
    url = f"https://svoy-narcolog.ru/uslugi/{service_slug}/"
    if fix_file(path, "Иваново", service_name, url):
        changed.append(path.relative_to(ROOT).as_posix())
        print("ok", path.relative_to(ROOT))

print("TOTAL", len(changed))

# CSS: style city crumb like muted intermediate (not current)
css_path = ROOT / "assets/css/components/hero.css"
css = css_path.read_text(encoding="utf-8")
if ".hero__breadcrumbs-city" not in css:
    # Insert after .hero__breadcrumbs-current block if present
    city_rule = """
.hero__breadcrumbs-city {
  color: inherit;
}
"""
    if ".hero__breadcrumbs-current" in css:
        css = css.replace(
            ".hero__breadcrumbs-current",
            city_rule.strip() + "\n\n.hero__breadcrumbs-current",
            1,
        )
    else:
        css += "\n" + city_rule
    css_path.write_text(css, encoding="utf-8", newline="\n")
    changed.append("assets/css/components/hero.css")
    print("ok assets/css/components/hero.css")


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

# spot-check
sample = (ROOT / "uslugi/vyzov-narkologa/shuya/index.html").read_text(encoding="utf-8")
assert "hero__breadcrumbs-city\">Шуя" in sample
assert "hero__breadcrumbs-current\">Вызов нарколога на дом" in sample
assert 'href="/uslugi/vyzov-narkologa/"' not in NAV_RE.search(sample).group(0)
print("spot-check ok")
