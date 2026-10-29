#!/usr/bin/env python3
"""音声・画像フォルダを走査して meta.json を生成（上書き）します。出力ファイルは meta.json だけです。

■ フォルダ構成（すべて soundtrack.html と同じ場所に置く）
  soundtrack.html
  make_tracks.py
  meta.json          ← このスクリプトが毎回上書き生成する（HTML がこれを読み込む）
  audio/
    disc1/           ← タブ「Disc 1」になる（フォルダ名 = Disc 番号。大文字小文字・スペースは無視）
      01_曲名.wav    ← 並び順はファイル名順。先頭の「01_」「01.」「01 - 」は曲名から消える
      02_曲名.mp3
    disc2/           ← タブ「Disc 2」
  images/            ← アイコン・ジャケットなど（任意。下記）
  （対応形式: wav / mp3 / ogg / flac / m4a）

■ meta.json の中身
  {
    "album": "アルバム名",
    "default_composer": "H@RM0NiA",          ← 編集OK: Composer が空の曲に使われる
    "images": { "emblem": "", "cover": "" },  ← 編集OK: 左上ロゴ / 共通ジャケット（画像パス）
    "staffroll": { "label": "Staff Roll", "video": "staffroll.mp4", "poster": "", "icon": "" },   ← 編集OK
    "omake": { "label": "おまけ", "url": "omake.html", "sound": "se/trophy.mp3",
               "title": "スタッフロール完走", "text": "「おまけ」が解放されました", "icon": "" }, ← 編集OK
    "discs": [
      {
        "id": "disc1", "name": "Disc 1",        ← 自動（フォルダ名から）
        "icon": "", "cover": "",                ← 編集OK: タブのアイコン / このDisc専用ジャケット
        "tracks": [
          {
            "file": "audio/disc1/01_曲名.wav",  ← 自動
            "title": "曲名",                    ← 自動（name があれば name、なければファイルのタグ、それも無ければファイル名）
            "name": "",                         ← 編集OK: 曲名を手動で付ける（track01.ogg などの曲に。空 → 自動の曲名）
            "duration": 105.32,                 ← 自動（秒。シークバーや曲リストの時間はこの値を使う）
            "composer": "",                     ← 編集OK: 空 → default_composer
            "arrange": false,                   ← 編集OK: true でアレンジ曲（Arrange バッジ表示）
            "original": "",                     ← 編集OK: 原作名（arrange が true のときだけ表示）
            "original_song": ""                 ← 編集OK: 原曲名（arrange が true のときだけ表示）
          }
        ]
      }
    ]
  }
  ・「自動」の項目は実行のたびに最新の内容で上書きされる（編集しても戻る）
  ・「編集OK」の項目は、手で編集するか、下記のコマンド（-i / --track）で設定する。前回の meta.json の内容が引き継がれる。曲は「file」で、Disc は「id」で対応づける
  ・ファイルを削除・改名した曲は meta.json から消える（改名した曲の属性は引き継がれないので注意）
  ・mp3 等に Composer タグがあれば、新しく追加された曲の composer の初期値に使われる
  ・以前の audio/meta.json（旧形式）があり、直下に meta.json が無い場合は、その内容を引き継いで作り直す

■ 曲ごとの属性（Composer・アレンジなど）をこのスクリプトで設定する
  meta.json を手で編集するほか、次のコマンドでも設定できます（設定は meta.json に保存され、次回以降も引き継がれる）。
  方法A) 対話モード: 曲の一覧から番号を選び、質問に答えていく
      python make_tracks.py -i
        → 曲の番号（例: 3 / 1,3 / 2-4 / all）を入力 → Composer、アレンジ曲か(y/n)、原作名、原曲名 を順に入力
        → Enter だけで「変更なし」、 - だけを入力すると「空にする」
  方法C) CSV で一括設定（track01.ogg 〜 など、全曲に名前・Composer・アレンジ情報を付けるとき便利）
      python make_tracks.py --export-csv tracks.csv   # 全曲の一覧を CSV に書き出す（Excel / メモ帳で編集）
      （tracks.csv の name / composer / arrange / original / original_song 列を埋めて保存。file 列は変えない）
      python make_tracks.py --import-csv tracks.csv   # CSV の内容を反映して meta.json を出力
      ・CSV の内容がそのまま反映される（空欄 = 空にする）。original / original_song が入っている行は arrange 欄が false でも true になる
      ・CSV に載っていない曲は変更されない。文字コードは UTF-8（BOM 付き）
  方法B) コマンドで直接指定
      python make_tracks.py --track "disc2/01_曲名.wav" arrange=true original="東方紅魔郷" original_song="明治十七年の上海アリス"
      python make_tracks.py --track disc2:3 composer="別の作曲者"     # Disc 2 の3曲目
      python make_tracks.py --track disc2 arrange=true                # Disc 2 の全曲（disc2:* でも同じ）
      ・曲の指定: ファイルのパス（末尾だけでも可）/ 曲名 / disc2:3（Discの何曲目か）/ disc2 または disc2:*（Discの全曲）
        複数の曲に当てはまるときはエラーになり、候補が表示される
      ・キー: name(曲名) / composer / arrange(true・false) / original(原作名) / original_song(原曲名)。1つの --track に複数並べてよい
      ・original か original_song を入れて arrange を指定しなかった場合は、arrange=true を自動で付ける
      ・値を空にするには  original=  のように右辺を空にする。--track は何度でも書ける
  ※ meta.json はこの設定を反映したうえで上書き生成される

■ アイコン・画像の設定
  方法1) images/ フォルダに、決まった名前で画像を置いて実行するだけ（空の項目だけ自動で埋まる）
      emblem.png      左上のロゴ                  （logo.png でも可）
      cover.png       ジャケット（共通）          （jacket.png でも可）
      disc1.png       Disc 1 のタブアイコン       （disc1_icon.png でも可。disc2, disc3… も同様）
      disc1_cover.png Disc 1 専用のジャケット
      staffroll.png   「Staff Roll」タブのアイコン （staff.png でも可）
      omake.png       「おまけ」タブのアイコン
      ・拡張子は png / jpg / jpeg / webp / gif / svg。大文字小文字・「_」「-」「空白」は無視される
  ホームページ(home.html)の左側に流す GIF:
      images/gif/ に GIF を置いて実行すると、名前順（1, 2, 10 の順。数字は数として並べる）に meta.json の "gifs" へ入る
      （毎回自動で作り直される。GIF が1枚もなければ、ホームの左側は通常のジャケット画像のまま）
  方法2) コマンドで直接指定（meta.json の値を上書きする）
      python make_tracks.py --icon staffroll=images/sr.png --icon omake=images/gift.png
      指定できるキー: emblem / cover / staffroll / omake / disc1 / disc1_cover / disc2 / disc2_cover …
      空に戻したいときは  --icon staffroll=   （右辺を空にする）

■ 使い方
  pip install mutagen
  python make_tracks.py                      # audio/ と images/ を走査して meta.json を上書き
  python make_tracks.py my_audio             # 音声フォルダ名を変えたい場合
  python make_tracks.py --images my_images   # 画像フォルダ名を変えたい場合
  曲や画像を追加・変更したら再実行する。
  ※ HTML は meta.json を読み込むため、ファイルを直接ダブルクリックして開く（file://）と動きません。
    GitHub Pages などに置くか、このフォルダで  python serve.py  を実行して
    http://localhost:8000/ を開いてください（index.html が開きます）。
    （python -m http.server は音声のシークに必要な Range リクエストに対応しておらず、曲の長さやシークバーが
      ずれる原因になるので、付属の serve.py を使ってください）
"""
import argparse, copy, csv, json, re, sys, unicodedata
from pathlib import Path
from mutagen import File

BASE = Path(__file__).resolve().parent        # soundtrack.html と同じフォルダ
META = BASE / "meta.json"
EXTS = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}
IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

ap = argparse.ArgumentParser(description="音声・画像フォルダを走査して meta.json を生成（上書き）")
ap.add_argument("audio", nargs="?", default="audio", help="音声フォルダ（既定: audio）")
ap.add_argument("--images", default="images", help="画像フォルダ（既定: images）")
ap.add_argument("--icon", action="append", default=[], metavar="KEY=PATH",
                help="画像を直接指定（例: staffroll=images/sr.png）。何度でも指定可")
ap.add_argument("--track", action="append", nargs="+", default=[], metavar="ARG",
                help="曲の属性を設定: --track 曲の指定 KEY=VALUE ...（例: --track disc2:1 arrange=true）")
ap.add_argument("--export-csv", metavar="PATH", help="全曲の属性を CSV に書き出す（Excel 等で一括編集用）")
ap.add_argument("--import-csv", metavar="PATH", help="CSV の内容を曲の属性に反映する（--export-csv で作った形式）")
ap.add_argument("-i", "--interactive", action="store_true", help="対話モードで曲の属性を設定")
args = ap.parse_args()
root = BASE / args.audio
img_dir = BASE / args.images
if not root.is_dir():
    sys.exit(f"フォルダが見つかりません: {root}")

def rel(p):   # HTML から見た相対パス
    try:
        return Path(p).resolve().relative_to(BASE).as_posix()
    except ValueError:
        return Path(p).as_posix()

nfc = lambda s: unicodedata.normalize("NFC", s)

DEFAULT_CFG = {
    "album": "夢違季節理論 ～ Mystic Season theory",
    "default_composer": "H@RM0NiA",
    "images": {"emblem": "", "cover": ""},
    "staffroll": {"label": "Staff Roll", "video": "staffroll.mp4", "poster": "", "icon": ""},
    "omake": {"label": "おまけ", "url": "omake.html", "sound": "se/trophy.mp3",
              "title": "スタッフロール完走", "text": "「おまけ」が解放されました", "icon": ""},
}

# ---------- 前回の meta.json（または旧形式 audio/meta.json）から引き継ぐ内容を読む ----------
cfg = copy.deepcopy(DEFAULT_CFG)
disc_cfg, track_cfg = {}, {}
old_path = META if META.exists() else (root / "meta.json" if (root / "meta.json").exists() else None)
if old_path:
    try:
        data = json.loads(old_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"{old_path} を読み込めません（JSONの書式エラー）: {e}")
    if old_path != META:
        print(f"旧形式の {rel(old_path)} の内容を引き継ぎます（不要になったら削除してかまいません）")
    for k in ("album", "default_composer"):
        if k in data: cfg[k] = data[k]
    for k in ("staffroll", "omake"):
        cfg[k].update(data.get(k) or {})
    im0 = data.get("images") or {}
    cfg["images"]["emblem"] = im0.get("emblem", "")
    cfg["images"]["cover"] = im0.get("cover", "")
    pick = lambda m: {k: m.get(k, v) for k, v in
                      (("name", ""), ("composer", ""), ("arrange", False), ("original", ""), ("original_song", ""))}
    if isinstance(data.get("discs"), list):                     # 新形式
        for d in data["discs"]:
            disc_cfg[d["id"]] = {"icon": d.get("icon", ""), "cover": d.get("cover", "")}
            for t in d.get("tracks", []):
                track_cfg[nfc(t["file"])] = pick(t)
    else:                                                        # 旧形式（audio/meta.json）
        for did, v in (im0.get("discs") or {}).items():
            disc_cfg[did] = {"icon": v.get("icon", ""), "cover": v.get("cover", "")}
        for k, v in (data.get("tracks") or {}).items():
            track_cfg[nfc(f"{rel(root)}/{k}")] = pick(v)

# ---------- 画像の登録 ----------
def norm(s):  # 大文字小文字・空白・_・- を無視して比較
    return re.sub(r"[\s_\-]", "", s.lower())

def find_image(names):
    if not img_dir.is_dir():
        return ""
    names = {norm(n) for n in names}
    for f in sorted(img_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in IMG_EXTS and norm(f.stem) in names:
            return rel(f)
    return ""

def autofill(box, key, names, label):
    if box.get(key):          # すでに設定済みなら何もしない
        return
    found = find_image(names)
    if found:
        box[key] = found
        print(f"画像を登録: {label} ← {found}")

im = cfg["images"]
autofill(im, "emblem", ["emblem", "logo"], "ロゴ(emblem)")
autofill(im, "cover", ["cover", "jacket"], "ジャケット(cover)")
autofill(cfg["staffroll"], "icon", ["staffroll", "staff"], "Staff Roll アイコン")
autofill(cfg["omake"], "icon", ["omake"], "おまけ アイコン")

for spec in args.icon:    # --icon KEY=PATH（明示指定。既存の値を上書き）
    if "=" not in spec:
        sys.exit(f"--icon は KEY=PATH の形で指定してください: {spec}")
    key, path = (x.strip() for x in spec.split("=", 1))
    if path and not (BASE / path).exists():
        print(f"※ 画像が見つかりません（パスだけ登録します）: {path}")
    k = norm(key)
    if k == "emblem":    im["emblem"] = path
    elif k == "cover":   im["cover"] = path
    elif k in ("staffroll", "staff"):  cfg["staffroll"]["icon"] = path
    elif k == "omake":   cfg["omake"]["icon"] = path
    else:
        m = re.fullmatch(r"(.+?)(cover)?", k)
        base, is_cover = m.group(1), bool(m.group(2))
        if base.endswith("icon"): base = base[:-4]
        names = {norm(g.name): g.name for g in root.iterdir() if g.is_dir()}
        did = names.get(base, base)
        disc_cfg.setdefault(did, {"icon": "", "cover": ""})["cover" if is_cover else "icon"] = path
    print(f"--icon: {key} = {path or '(空)'}")

# ---------- 音声フォルダの走査 ----------
def tag(audio, keys):
    tags = getattr(audio, "tags", None)
    if not tags:
        return None
    for k in keys:
        try:
            v = tags[k]
            v = v.text[0] if hasattr(v, "text") else (v[0] if isinstance(v, list) else v)
            if str(v).strip():
                return str(v).strip()
        except Exception:
            pass
    return None

def strip_num(s):
    return re.sub(r"^\d+\s*[-_.．\s]+\s*", "", s) or s

def disc_no(p):  # "disc1" / "Disc 2" → 1 / 2、それ以外は None
    m = re.fullmatch(r"disc\s*[-_]?\s*(\d+)", p.name, re.I)
    return int(m.group(1)) if m else None

dirs = [p for p in root.iterdir() if p.is_dir()]
discs_dirs = sorted((p for p in dirs if disc_no(p) is not None), key=disc_no)
others = sorted(p for p in dirs if disc_no(p) is None)
if others:
    print("※ discN 以外のフォルダは別タブとして末尾に追加します:", ", ".join(p.name for p in others))
groups = discs_dirs + others or [root]

out_discs, seen, new_tracks, auto_titles = [], set(), 0, {}
for g in groups:
    tracks = []
    for f in sorted(g.iterdir(), key=lambda p: p.name):
        if f.suffix.lower() not in EXTS:
            continue
        a = File(f)
        if a is None or not a.info:
            print("読み込めません:", f); continue
        src = rel(f)
        key = nfc(src); seen.add(key)
        if key in track_cfg:
            c = track_cfg[key]
        else:                                  # 新しい曲 → 雛形（タグにComposerがあれば初期値に）
            c = {"name": "", "composer": tag(a, ("TCOM", "composer", "\xa9wrt")) or "",
                 "arrange": False, "original": "", "original_song": ""}
            new_tracks += 1
        auto = tag(a, ("TIT2", "title", "\xa9nam")) or strip_num(f.stem)
        auto_titles[src] = auto
        tracks.append({"file": src,
                       "title": c["name"] or auto,
                       "name": c["name"],
                       "duration": round(a.info.length, 2),
                       "composer": c["composer"], "arrange": bool(c["arrange"]),
                       "original": c["original"], "original_song": c["original_song"]})
    if tracks:
        n = disc_no(g)
        name = f"Disc {n}" if n is not None else (strip_num(g.name) if g != root else "Disc 1")
        did = g.name if g != root else "disc1"
        d = disc_cfg.setdefault(did, {"icon": "", "cover": ""})
        autofill(d, "icon", [did, did + "icon"], f"{did} タブアイコン")
        autofill(d, "cover", [did + "cover"], f"{did} ジャケット")
        out_discs.append({"id": did, "name": name, "icon": d["icon"], "cover": d["cover"], "tracks": tracks})
        print(f"{g.name} → {name}: {len(tracks)}曲")

# ---------- 曲ごとの属性の設定（--track / -i） ----------
FIELDS = {"name": "name", "title": "name", "composer": "composer", "arrange": "arrange", "original": "original", "orig": "original",
          "original_song": "original_song", "song": "original_song"}
TRUE = {"true", "1", "yes", "y", "on", "はい", "あり", "○"}
FALSE = {"false", "0", "no", "n", "off", "いいえ", "なし", "×", ""}

def to_bool(v):
    s = str(v).strip().lower()
    if s in TRUE: return True
    if s in FALSE: return False
    sys.exit(f"arrange には true / false を指定してください: {v}")

def all_tracks():
    return [(d, t) for d in out_discs for t in d["tracks"]]

def resolve(spec):
    """曲の指定 → 該当する曲(dict)のリスト"""
    s = nfc(spec.strip())
    by_id = {norm(d["id"]): d for d in out_discs}
    m = re.fullmatch(r"(.+?):(\*|\d+)", s)
    if m and norm(m.group(1)) in by_id:                       # disc2:3 / disc2:*
        d = by_id[norm(m.group(1))]
        if m.group(2) == "*": return list(d["tracks"])
        i = int(m.group(2))
        if not 1 <= i <= len(d["tracks"]):
            sys.exit(f"{d['id']} は 1〜{len(d['tracks'])} 曲目です: {spec}")
        return [d["tracks"][i - 1]]
    if norm(s) in by_id:                                       # disc2（Discの全曲）
        return list(by_id[norm(s)]["tracks"])
    ts = [t for _, t in all_tracks()]
    for hit in ([t for t in ts if nfc(t["file"]) == s],
                [t for t in ts if nfc(t["file"]).endswith("/" + s)],
                [t for t in ts if nfc(t["title"]) == s]):
        if len(hit) == 1: return hit
        if len(hit) > 1:
            sys.exit(f"「{spec}」に当てはまる曲が複数あります。もう少し詳しく指定してください:\n  " +
                     "\n  ".join(t["file"] for t in hit))
    sys.exit(f"曲が見つかりません: {spec}\n（audio/ 内の曲: " + ", ".join(t["file"] for _, t in all_tracks()[:5]) + " ...）")

def set_attrs(t, kv):
    if ("original" in kv or "original_song" in kv) and "arrange" not in kv \
            and any(kv.get(k) for k in ("original", "original_song")) and not t["arrange"]:
        kv = {**kv, "arrange": True}
        print(f"  （original/original_song が指定されたので arrange=true にしました: {t['file']}）")
    for k, v in kv.items():
        t[k] = to_bool(v) if k == "arrange" else str(v)
    if "name" in kv:                                           # name が空なら自動の曲名に戻る
        t["title"] = t["name"] or auto_titles.get(t["file"], t["title"])
    print("設定:", t["file"], " ", ", ".join(f"{k}={t[k]!r}" for k in kv))


# ---------- CSV で一括設定（--import-csv / --export-csv） ----------
CSV_COLS = ["file", "name", "composer", "arrange", "original", "original_song"]

def import_csv(path):
    p = Path(path)
    if not p.is_file():
        sys.exit(f"CSV が見つかりません: {path}")
    n = 0
    with p.open(encoding="utf-8-sig", newline="") as fp:
        for row in csv.DictReader(fp):
            f = nfc((row.get("file") or "").strip())
            if not f: continue
            hit = [t for _, t in all_tracks() if nfc(t["file"]) == f]
            if not hit:
                print(f"※ CSV の曲が見つかりません（スキップ）: {f}"); continue
            kv = {k: (row.get(k) or "").strip() for k in ("name", "composer", "original", "original_song")}
            a = (row.get("arrange") or "").strip()
            has_orig = bool(kv["original"] or kv["original_song"])
            if has_orig:                      # 原作名・原曲名があれば、arrange 欄が false/空でもアレンジ曲にする
                kv["arrange"] = "true"
            else:
                kv["arrange"] = a or "false"
            set_attrs(hit[0], kv); n += 1
    print(f"CSV から {n} 曲を反映しました: {path}")

def export_csv(path):
    with Path(path).open("w", encoding="utf-8-sig", newline="") as fp:
        w = csv.writer(fp); w.writerow(CSV_COLS)
        for _, t in all_tracks():
            w.writerow([t["file"], t["name"], t["composer"], "true" if t["arrange"] else "false",
                        t["original"], t["original_song"]])
    print(f"CSV を書き出しました: {path}（title が自動のままの曲は name 欄が空です）")

if args.import_csv:
    import_csv(args.import_csv)

for spec_args in args.track:                                   # --track
    spec, *pairs = spec_args
    kv = {}
    for pr in pairs:
        if "=" not in pr:
            sys.exit(f"--track は「曲の指定 KEY=VALUE ...」の形で指定してください: {pr}")
        k, v = pr.split("=", 1)
        if k.strip().lower() not in FIELDS:
            sys.exit(f"使えるキーは name / composer / arrange / original / original_song です: {k}")
        kv[FIELDS[k.strip().lower()]] = v
    if not kv:
        sys.exit(f"--track {spec} に設定する KEY=VALUE がありません")
    for t in resolve(spec):
        set_attrs(t, dict(kv))

def interactive():                                             # -i
    flat = all_tracks()
    while True:
        print("\n---- 曲の一覧 ----")
        for n, (d, t) in enumerate(flat, 1):
            extra = f"  ★Arrange  原作: {t['original'] or '-'} / 原曲: {t['original_song'] or '-'}" if t["arrange"] else ""
            print(f"{n:3d}. [{d['id']}] {t['title']}   Composer: {t['composer'] or '(既定)'}{extra}")
        try:
            s = input("\n設定する曲の番号（例: 3 / 1,3 / 2-4 / all、Enterで終了）: ").strip()
        except EOFError:
            break
        if not s: break
        idx = set()
        try:
            for part in s.split(","):
                part = part.strip()
                if part.lower() == "all": idx |= set(range(1, len(flat) + 1))
                elif "-" in part:
                    a, b = part.split("-", 1); idx |= set(range(int(a), int(b) + 1))
                else: idx.add(int(part))
            if not idx or min(idx) < 1 or max(idx) > len(flat): raise ValueError
        except ValueError:
            print("番号の指定が正しくありません"); continue
        targets = [flat[i - 1][1] for i in sorted(idx)]
        one = targets[0] if len(targets) == 1 else None
        shown = lambda k: f" 現在: {one[k] or '(空)'}" if one else ""
        print(f"{len(targets)}曲を設定します（Enter=変更なし / - =空にする）")
        kv = {}
        def ask(label, key):
            v = input(f"  {label}{shown(key)} → ").strip()
            if v == "-": kv[key] = ""
            elif v: kv[key] = v
        try:
            ask("曲名 (Name)", "name")
            ask("Composer", "composer")
            a = input(f"  アレンジ曲ですか？ y/n{' 現在: ' + ('y' if one['arrange'] else 'n') if one else ''} → ").strip()
            if a: kv["arrange"] = to_bool(a)
            if kv.get("arrange") is True or ("arrange" not in kv and any(t["arrange"] for t in targets)):
                ask("原作名 (Original)", "original")
                ask("原曲名 (Original Song)", "original_song")
        except EOFError:
            break
        for t in targets:
            if kv: set_attrs(t, dict(kv))
if args.interactive:
    interactive()
if args.export_csv:
    export_csv(args.export_csv)

gone = [k for k in track_cfg if k not in seen]
if gone:
    print(f"※ 音声ファイルが見つからないため meta.json から削除した曲: {len(gone)} 件")
    for k in gone: print("   ", k)

# images/gif/ の GIF を名前順（数字は数として）に並べる ※ホームページ左側のスライドショー用
gif_dir = img_dir / "gif"
natural = lambda f: [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", f.name)]
gifs = [rel(f) for f in sorted(gif_dir.iterdir(), key=natural)
        if f.is_file() and f.suffix.lower() == ".gif"] if gif_dir.is_dir() else []
if gifs:
    print(f"GIFを登録: {len(gifs)}枚（{gif_dir.name}/ 内、名前順）")

out = {"_readme": "このファイルは make_tracks.py が実行のたびに上書き生成します。書き方は make_tracks.py の冒頭を参照。",
       **cfg, "gifs": gifs, "discs": out_discs}
META.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"meta.json を出力しました（新しい曲 {new_tracks} 曲）")
