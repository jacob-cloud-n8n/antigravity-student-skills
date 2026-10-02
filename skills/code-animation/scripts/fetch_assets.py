#!/usr/bin/env python3
"""下載 references/assets.json 列的函式庫、字型與 CC0 素材到本機素材庫，並做安全檢查與 sha256 釘選。

用法：python3 fetch_assets.py            # 下載缺的、驗已有的（可重複執行）
素材庫位置：~/.local/share/code-animation-assets/（Windows＝C:\\Users\\<你>\\.local\\share\\code-animation-assets）
  lib/<套件>/   函式庫（只取 pick 列的檔案；不執行 npm install、不跑任何套件腳本）
  <id>/         字型、音效、角色 SVG
檢查：
  - npm 套件：package.json 不得有 preinstall／install／postinstall
  - SVG：含 <script、on*= 事件、外部 href、<foreignObject 一律拒收（SVG 可夾帶程式）
  - zip：只允許音訊與說明文字檔；作業系統雜檔（desktop.ini 等）略過不解；防路徑穿越
  - sha256：清單為空＝首次下載寫入（信任首次取得）；之後不符就中止
"""
import os, re, io, json, hashlib, tarfile, zipfile, urllib.request, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAN = HERE.parent / "references" / "assets.json"
OK_EXT = {".ogg", ".wav", ".mp3", ".txt", ".md", ".url", ""}
SKIP = {"desktop.ini", ".DS_Store", "Thumbs.db"}
BAD_SVG = re.compile(r"<script|\son\w+\s*=|(?:xlink:)?href\s*=\s*[\"']https?:|<foreignObject", re.I)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def pin(rec, data, label):
    h = hashlib.sha256(data).hexdigest()
    if rec.get("sha256") and rec["sha256"] != h:
        sys.exit(f"sha256 不符，中止（來源內容變了，先人工確認）：{label}")
    rec["sha256"] = h


def cached(path, url):
    return (path.read_bytes(), False) if path.exists() else (get(url), True)


def main():
    m = json.load(open(MAN, encoding="utf-8"))
    dest = Path(os.path.expanduser(m["dest"])); dest.mkdir(parents=True, exist_ok=True)
    new = ok = 0
    for p in m["packs"]:
        kind = p["type"]
        if kind == "npm":
            d = dest / "lib" / p["id"].replace("lib-", ""); d.mkdir(parents=True, exist_ok=True)
            tgz = d / os.path.basename(p["url"])
            data, fresh = cached(tgz, p["url"]); pin(p, data, p["id"])
            with tarfile.open(fileobj=io.BytesIO(data)) as t:
                pkg = json.load(t.extractfile("package/package.json"))
                bad = set(pkg.get("scripts", {})) & {"preinstall", "install", "postinstall"}
                if bad: sys.exit(f"{p['id']} 含安裝腳本 {bad}，拒收")
                for name in p["pick"]:
                    (d / os.path.basename(name)).write_bytes(t.extractfile(name).read())
            if fresh: tgz.write_bytes(data); new += 1
            else: ok += 1
        elif kind == "files":
            d = dest / p["id"]; d.mkdir(parents=True, exist_ok=True)
            for f in p["files"]:
                path = d / f["name"]
                data, fresh = cached(path, f["url"])
                if path.suffix.lower() == ".svg" and BAD_SVG.search(data.decode("utf-8", "ignore")):
                    sys.exit(f"SVG 含可執行內容或外部連結，拒收：{f['url']}")
                pin(f, data, f["name"])
                if fresh: path.write_bytes(data); new += 1
                else: ok += 1
        elif kind == "zip":
            d = dest / p["id"]; d.mkdir(parents=True, exist_ok=True)
            zpath = d / os.path.basename(p["url"])
            data, fresh = cached(zpath, p["url"]); pin(p, data, p["id"])
            if fresh: zpath.write_bytes(data); new += 1
            else: ok += 1
            with zipfile.ZipFile(zpath) as z:
                names = [i for i in z.namelist() if not i.endswith("/") and os.path.basename(i) not in SKIP]
                bad = [i for i in names if os.path.splitext(i)[1].lower() not in OK_EXT]
                if bad: sys.exit(f"zip 含不允許的檔案類型，拒收：{p['id']} → {bad[:5]}")
                root = str(d.resolve()) + os.sep
                for i in names:
                    if not str((d / i).resolve()).startswith(root): sys.exit(f"zip 路徑穿越，拒收：{i}")
                z.extractall(d, members=names)
        else:
            sys.exit(f"未知類型：{kind}")
    json.dump(m, open(MAN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"OK 新下載 {new}、已存在並驗過 {ok} → {dest}")


if __name__ == "__main__":
    main()
