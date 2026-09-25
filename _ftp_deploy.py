import ftplib
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

HOST = "koroleld.beget.tech"
USER = "koroleld"
PASS = "Qetuosfhk12-//:"
REMOTE_ROOT = "svoy-narcolog.ru/public_html"
LOCAL = Path(r"C:\svoy-narcolog-cities.ru")

SKIP_DIRS = {
    ".git",
    ".cursor",
    "node_modules",
    "__pycache__",
    "agent-transcripts",
}
SKIP_NAMES = {
    ".DS_Store",
    "Thumbs.db",
    ".gitignore",
    ".gitattributes",
    "AGENTS.md",
    "README.md",
    "_ftp_deploy.py",
    "composer.phar",
}
SKIP_SUFFIXES = {".part", ".log", ".pyc", ".py", ".md", ".pdf"}

# Laravel leftovers that must not remain as document root entrypoints
DELETE_REMOTE = {
    "index.php",
}

uploaded = 0
skipped = 0
deleted = 0
errors = []


def reconnect():
    for attempt in range(1, 10):
        try:
            ftp = ftplib.FTP(HOST, timeout=120)
            ftp.login(USER, PASS)
            ftp.encoding = "utf-8"
            ftp.set_pasv(True)
            print(f"Connected (attempt {attempt})")
            return ftp
        except Exception as e:
            print(f"Connect fail {attempt}: {e}")
            time.sleep(2 * attempt)
    raise RuntimeError("Cannot connect to FTP")


def should_skip(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    name = Path(rel).name
    if name in SKIP_NAMES:
        return True
    if any(name.endswith(sfx) for sfx in SKIP_SUFFIXES):
        return True
    for s in SKIP_DIRS:
        if rel == s or rel.startswith(s + "/"):
            return True
    return False


def ensure_dir(ftp, remote_dir: str):
    parts = remote_dir.replace("\\", "/").strip("/").split("/")
    path = ""
    for part in parts:
        path = f"{path}/{part}" if path else part
        try:
            ftp.mkd(path)
        except Exception:
            pass


def remote_size(ftp, rpath: str):
    try:
        return ftp.size(rpath)
    except Exception:
        return None


def upload_file(ftp, lpath: Path, rpath: str, force: bool = False):
    global uploaded, skipped
    ensure_dir(ftp, str(Path(rpath).parent).replace("\\", "/"))
    local_size = lpath.stat().st_size
    remote = remote_size(ftp, rpath)

    critical = any(
        x in rpath.replace("\\", "/")
        for x in (
            "/.htaccess",
            "/send.php",
            "/index.html",
            "/assets/js/",
            "/assets/css/",
            "/robots.txt",
            "/sitemap.xml",
            "/404.html",
        )
    )

    if not force and remote is not None and remote == local_size and not critical:
        skipped += 1
        return ftp

    for attempt in range(1, 6):
        try:
            with open(lpath, "rb") as f:
                ftp.storbinary(f"STOR {rpath}", f, blocksize=64 * 1024)
            uploaded += 1
            if uploaded % 25 == 0:
                print(f"... uploaded {uploaded}, skipped {skipped}")
            return ftp
        except Exception as e:
            print(f"RETRY {attempt} {rpath}: {e}")
            try:
                ftp.quit()
            except Exception:
                pass
            time.sleep(1.5 * attempt)
            ftp = reconnect()
    errors.append(rpath)
    return ftp


def walk_upload(ftp, local_dir: Path, remote_dir: str, rel: str = ""):
    if should_skip(rel):
        print(f"SKIP DIR {rel}")
        return ftp

    ensure_dir(ftp, remote_dir)

    for entry in sorted(local_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        name = entry.name
        rel_path = f"{rel}/{name}".strip("/") if rel else name
        rpath = f"{remote_dir}/{name}"

        if entry.is_dir():
            if should_skip(rel_path):
                print(f"SKIP DIR {rel_path}")
                continue
            print(f"DIR  {rel_path}")
            ftp = walk_upload(ftp, entry, rpath, rel_path)
        else:
            if should_skip(rel_path):
                continue
            ftp = upload_file(ftp, entry, rpath)
    return ftp


def delete_laravel_entrypoints(ftp):
    global deleted
    for name in DELETE_REMOTE:
        rpath = f"{REMOTE_ROOT}/{name}"
        try:
            ftp.delete(rpath)
            deleted += 1
            print(f"DELETED {rpath}")
        except Exception as e:
            print(f"DELETE skip {rpath}: {e}")
    return ftp


def main():
    print(f"Uploading static site to {REMOTE_ROOT}")
    ftp = reconnect()
    ftp = walk_upload(ftp, LOCAL, REMOTE_ROOT)
    ftp = delete_laravel_entrypoints(ftp)

    try:
        ftp.quit()
    except Exception:
        pass

    print(
        f"DONE uploaded={uploaded} skipped={skipped} deleted={deleted} errors={len(errors)}"
    )
    for e in errors[:40]:
        print("ERR", e)


if __name__ == "__main__":
    main()
