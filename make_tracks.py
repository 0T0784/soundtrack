#!/usr/bin/env python3
"""音声・画像フォルダを走査して meta.json（HTML が読み込む自動生成ファイル）を作ります。
手で編集する設定は config.json に保存されます（meta.json は実行のたびに作り直されるので、直接は編集しません）。

■ フォルダ構成（すべて soundtrack.html と同じ場所に置く）
  soundtrack.html
  make_tracks.py
  config.json        ← 設定ファイル。手で編集してよい（アルバム名・スタッフ・曲名・アレンジ設定など）。GitHub にはこちらを置く
  meta.json          ← 自動生成（config.json + 曲の長さ・ストーリー・GIF など）。HTML がこれを読み込む。GitHub には置かない（.gitignore に書く）
  make_staff.py      ← スタッフロールのスタッフ一覧を書いて staff.json に出力するプログラム（任意。下記「スタッフ一覧」）
  staff.json         ← make_staff.py が自動生成（あれば meta.json のスタッフ欄に使われる）。GitHub には置かない（.gitignore に書く）
  audio/
    disc1/           ← タブ「Disc 1」になる（フォルダ名 = Disc 番号。大文字小文字・スペースは無視）
      01_曲名.wav    ← 並び順はファイル名順。先頭の「01_」「01.」「01 - 」は曲名から消える
      02_曲名.mp3
    disc2/           ← タブ「Disc 2」
  images/            ← アイコン・ジャケットなど（任意。下記）
  （対応形式: wav / mp3 / ogg / flac / m4a）

■ config.json と meta.json の中身
  config.json は下の「編集OK」の項目だけ、meta.json は「自動」の項目も含めたもの（HTML が読むのは meta.json）です。
  最初は meta.json だけでも動きます（初回の実行で、その内容から config.json が作られます）。
  {
    "album": "アルバム名",
    "default_composer": "0to784",          ← 編集OK: Composer が空の曲に使われる
    "images": { "emblem": "", "cover": "" },  ← 編集OK: 左上ロゴ / 共通ジャケット（画像パス）
    "staffroll": { "label": "Staff Roll", "video": "staffroll.mp4", "poster": "", "icon": "" },   ← 編集OK
    "omake": { "label": "おまけ", "url": "omake.html", "sound": "se/trophy.mp3",
               "title": "スタッフロール完走", "text": "左下のアイコンから「おまけ」を読めます", "icon": "" }, ← 編集OK: スタッフロールを最後まで見ると、左下に「おまけ」のアイコンが出る（押すと url へ移動）
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
            "original_song": "",                ← 編集OK: 原曲名（arrange が true のときだけ表示）
            "story": "stories/disc1/track01.txt"  ← 自動（stories/ に同名の .txt があるときだけ。下の「ストーリー」を参照）
          }
        ]
      }
    ]
  }
  ・「自動」の項目は実行のたびに最新の内容で上書きされる（編集しても戻る）
  ・「編集OK」の項目は、config.json を手で編集するか、下記のコマンド（-i / --track）で設定する。config.json の内容が引き継がれる。曲は「file」で、Disc は「id」で対応づける
  ・ファイルを削除・改名した曲は config.json から消える（改名した曲の属性は引き継がれないので注意）
  ・mp3 等に Composer タグがあれば、新しく追加された曲の composer の初期値に使われる
  ・以前の audio/meta.json（旧形式）があり、直下に config.json も meta.json も無い場合は、その内容を引き継いで作り直す

■ 曲ごとの属性（Composer・アレンジなど）をこのスクリプトで設定する
  config.json を手で編集するほか、次のコマンドでも設定できます（設定は config.json に保存され、次回以降も引き継がれる）。
  方法A) 対話モード: 曲の一覧から番号を選び、質問に答えていく
      python make_tracks.py -i
        → 曲の番号（例: 3 / 1,3 / 2-4 / all）を入力 → Composer、アレンジ曲か(y/n)、原作名、原曲名 を順に入力
        → Enter だけで「変更なし」、 - だけを入力すると「空にする」
  方法C) CSV で一括設定（track01.ogg 〜 など、全曲に名前・Composer・アレンジ情報を付けるとき便利）
      ★ 実行すると、同じフォルダの tracks.csv を自動で参照します（--import-csv の指定は不要）
      1. python make_tracks.py を実行 → tracks.csv が自動で作られる（全曲の一覧。Excel / メモ帳で開ける）
      2. tracks.csv の name / composer / arrange / original / original_song 列を埋めて保存（file 列は変えない。
         title_now 列は「今の曲名」を見るための参考用で、編集しても反映されない）
      3. もう一度実行 → CSV の内容が config.json に反映され、tracks.csv も最新の内容で書き直される
      ・CSV と config.json の「更新日時が新しい方」を優先する: CSV を保存し直したあとなら CSV の内容を反映し、
        config.json を手で直したあとなら CSV は反映せず、config.json の内容で CSV を書き直す
      ・original（原作）欄は、1行目にサークル名、2行目に作品名のように改行して書ける（Excel ではセル内改行 Alt+Enter。コマンドでは \n と書く）
      ・CSV の内容がそのまま反映される（空欄 = 空にする）。original / original_song が入っている行は arrange 欄が false でも true になる
      ・CSV に載っていない曲は変更されない（新しい曲は実行後に CSV へ追加される）。文字コードは UTF-8（BOM 付き）
      ・Excel で tracks.csv を開いたままだと書き直せないので、閉じてから実行する（その旨の警告が出る）
      ・オプション: --csv 別名.csv（参照するCSVを変える） / --no-csv（CSV を使わない）
      ・--import-csv 名前.csv で更新日時に関係なく強制的に反映、--export-csv 名前.csv で別の場所にも書き出せる
  方法B) コマンドで直接指定
      python make_tracks.py --track "disc2/01_曲名.wav" arrange=true original="東方紅魔郷" original_song="明治十七年の上海アリス"
      python make_tracks.py --track disc2:3 composer="別の作曲者"     # Disc 2 の3曲目
      python make_tracks.py --track disc2 arrange=true                # Disc 2 の全曲（disc2:* でも同じ）
      ・曲の指定: ファイルのパス（末尾だけでも可）/ 曲名 / disc2:3（Discの何曲目か）/ disc2 または disc2:*（Discの全曲）
        複数の曲に当てはまるときはエラーになり、候補が表示される
      ・キー: name(曲名) / composer / arrange(true・false) / original(原作名) / original_song(原曲名)。1つの --track に複数並べてよい
      ・original か original_song を入れて arrange を指定しなかった場合は、arrange=true を自動で付ける
      ・値を空にするには  original=  のように右辺を空にする。--track は何度でも書ける
  ※ 設定は config.json に保存され、meta.json もそれを反映して作り直される

■ 音声ファイルのタグ（ORIGINAL など）からアレンジ曲を自動判定
  mp3 / ogg / flac / m4a / wav のタグに ORIGINAL 系の項目が入っていれば、読み込んで original / original_song / arrange に反映します。
      ORIGINAL           → 原曲名（original_song）          ※ ORIGINAL TITLE / ORIGINAL SONG でも可
      ORIGINAL COMPOSER  → 原作者・サークル名（original の1行目）    ※ ORIGINAL ARTIST / TOPE（mp3の「原アーティスト」）でも可
      ORIGINAL ALBUM     → 原作名（original の2行目）               ※ ORIGINAL WORK / ORIGINAL GAME / TOAL でも可
      （ORIGINAL_COMPOSER のように _ でつないだ名前や、大文字小文字の違いは同じものとして扱う）
      例: ORIGINAL COMPOSER=上海アリス幻樂団, ORIGINAL ALBUM=東方怪綺談
          → プレイヤーの Original 欄に「上海アリス幻樂団」の下の行に「東方怪綺談」と表示される
  ・どれか1つでも入っていれば arrange=true（アレンジ曲）にします。1つも無い曲は今のまま（勝手に false にはしません）
  ・新しく追加した曲は、実行するだけで自動で読み込みます
  ・すでに登録済みの曲にも読み込みたいときは --tags を付けて実行:
      python make_tracks.py --tags               # 空欄の項目だけタグで埋める（手で入れた値は残す）
      python make_tracks.py --tags overwrite     # タグの内容で上書きする
  ・タグの名前の対応を変えたいときは、このファイルの TAG_ORIG_SONG / TAG_ORIG_COMPOSER / TAG_ORIG_WORK を編集する

■ ストーリー（曲ごとの手記）
  曲ごとのストーリーは、曲と同じ名前の .txt を stories/ フォルダに置くだけで登録されます（実行のたびに自動で探します）。
      stories/
        disc1/
          track01.txt    ← audio/disc1/track01.ogg のストーリー（曲のファイル名と同じ名前）
          02.txt         ← 「02.txt」「2.txt」のように Disc 内の曲番号でも可
        disc2/
          track01.txt
  ・文字コードは UTF-8。空行で段落が分かれ、行の途中の改行はそのまま表示される（全角スペースで字下げもできる）
  ・.txt が無い曲には何も出ない。ある曲には、曲リストに「Story」バッジと、右側に「ストーリーを読む」ボタンが付く
  ・meta.json の各曲の "story" に .txt のパスが入る（自動。編集しても実行のたびに作り直される）
  ・フォルダ名を変えたいとき: python make_tracks.py --stories 別名
  ・文章を直すだけなら make_tracks.py の再実行は不要（ページを再読み込みすれば反映される）

■ アイコン・画像の設定
  方法1) images/ フォルダに、決まった名前で画像を置いて実行するだけ（空の項目だけ自動で埋まる）
      emblem.png      左上のロゴ                  （logo.png でも可）
      cover.png       ジャケット（共通）          （jacket.png でも可）
      disc1.png       Disc 1 のタブアイコン       （disc1_icon.png でも可。disc2, disc3… も同様）
      disc1_cover.png Disc 1 専用のジャケット
      staffroll.png   「Staff Roll」タブのアイコン （staff.png でも可）
      omake.png       「おまけ」のアイコン（解放後、画面の左下に出る。無ければ🎁）
      ・拡張子は png / jpg / jpeg / webp / gif / svg。大文字小文字・「_」「-」「空白」は無視される
  ホームページ(home.html)の左側に流す GIF:
      images/gif/ に GIF を置いて実行すると、名前順（1, 2, 10 の順。数字は数として並べる）に meta.json の "gifs" へ入る
      （毎回自動で作り直される。GIF が1枚もなければ、ホームの左側は通常のジャケット画像のまま）
  スタッフロールのタブ: 下の再生バーが隠れ、右側にスタッフ紹介が出る（動画自身のコントロールで操作する）。
      スタッフ一覧は make_staff.py で書くのがおすすめ（下の「スタッフ一覧」）。config.json の "staffroll" の "staff" に直接書くこともできる（staff.json が無いときに使われる）:
        "staff": [
          { "name": "オト", "role": "作曲・制作", "text": "ひとこと（\n で改行できる）", "icon": "images/staff1.png" }
        ]
      ・role / text / icon は省略可。icon が無い・読めないときは🍂が出る。何も書かなければ書き方のヒントが出る
  スタッフロールを YouTube にする（mp4 の代わりに YouTube の動画を表示。下のプレイヤーのボタンで再生・シークもできる）:
      python make_tracks.py --youtube https://youtu.be/xxxxxxxxxxx      # リンク（watch?v= 形式や動画IDだけでも可）
      python make_tracks.py --youtube ""                                # mp4 に戻す
      ・meta.json の "staffroll" の "youtube" に書いてもよい。設定されていれば mp4 より優先される
      ・動画は「埋め込みを許可」にしておく（限定公開・公開は可、非公開は不可）
      ・YouTube は file:// では再生できないので、GitHub Pages か python serve.py で開く
  方法2) コマンドで直接指定（meta.json の値を上書きする）
      python make_tracks.py --icon staffroll=images/sr.png --icon omake=images/gift.png
      指定できるキー: emblem / cover / staffroll / omake / disc1 / disc1_cover / disc2 / disc2_cover …
      空に戻したいときは  --icon staffroll=   （右辺を空にする）

■ スタッフ一覧（make_staff.py → staff.json）
  スタッフロールのスタッフは、別のプログラム make_staff.py に書いて JSON に出力できます（改行つきのひとことも、そのまま改行して書ける）。
      1. make_staff.py の STAFF にスタッフを書く（name / role / text / icon。書き方は make_staff.py の冒頭を参照）
      2. python make_staff.py → staff.json ができる
      3. python make_tracks.py → staff.json の内容が meta.json の "staffroll" の "staff" に入る（HTML はこれまでどおり meta.json を読むだけ）
  ・スタッフロール動画の YouTube の URL も make_staff.py の YOUTUBE に書ける（staff.json 経由で meta.json の "youtube" に入る）
  ・staff.json があるときは、config.json に書いたスタッフ・YouTube より staff.json が優先される（config.json には書き込まれない）。--youtube 指定時はそちらが最優先
  ・staff.json が無ければ、これまでどおり config.json の "staff" が使われる
  ・make_staff.py を直したら make_tracks.py の前に毎回 make_staff.py を実行する（GitHub の deploy.yml は自動で両方実行する）
  ・オプション: --staff 別名.json（読み込む JSON を変える）

■ GitHub Pages（deploy.yml）で使うとき
  ・config.json はリポジトリに入れる。meta.json は自動生成なので入れない（.gitignore に meta.json と一行書く）
  ・staff.json も自動生成なので入れない（.gitignore に staff.json と書く。make_staff.py はリポジトリに入れる）
  ・deploy.yml が公開のたびに  python make_staff.py → python make_tracks.py --no-csv --no-config --tags  を実行して meta.json を作る
      --no-config : config.json は書き換えない（CI 用。パソコンでは付けない）
  ・初めて分けるとき: ① パソコンで python make_tracks.py を1回実行 → config.json ができる
      ② git rm --cached meta.json で meta.json をリポジトリから外し、.gitignore に meta.json を書く

■ 使い方
  pip install mutagen
  make_tracks.bat                            # Windows: ダブルクリックで実行（Python と mutagen が無ければ案内・自動インストール）
  python make_tracks.py                      # audio/ と images/ を走査して meta.json を上書き（tracks.csv も参照）
  python make_tracks.py my_audio             # 音声フォルダ名を変えたい場合
  python make_tracks.py --images my_images   # 画像フォルダ名を変えたい場合
  曲や画像を追加・変更したら再実行する。
  ※ HTML は meta.json を読み込むため、ファイルを直接ダブルクリックして開く（file://）と動きません。
    GitHub Pages などに置くか、このフォルダで  python serve.py  を実行して
    http://localhost:8000/ を開いてください（index.html が開きます）。
    （python -m http.server は音声のシークに必要な Range リクエストに対応しておらず、曲の長さやシークバーが
      ずれる原因になるので、付属の serve.py を使ってください）
"""
import argparse, copy, csv, json, os, re, sys, unicodedata
from pathlib import Path
from mutagen import File

BASE = Path(__file__).resolve().parent        # soundtrack.html と同じフォルダ
META = BASE / "meta.json"                      # 自動生成（HTML が読む）
CONFIG = BASE / "config.json"                  # 設定（手で編集してよい）
EXTS = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}
IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

ap = argparse.ArgumentParser(description="音声・画像フォルダを走査して meta.json を生成（上書き）")
ap.add_argument("audio", nargs="?", default="audio", help="音声フォルダ（既定: audio）")
ap.add_argument("--images", default="images", help="画像フォルダ（既定: images）")
ap.add_argument("--stories", default="stories", help="ストーリー(.txt)のフォルダ（既定: stories）")
ap.add_argument("--tags", nargs="?", const="fill", choices=["fill", "overwrite"],
                help="登録済みの曲にも、タグの ORIGINAL 系を読み込む（fill=空欄だけ埋める[既定] / overwrite=上書き）")
ap.add_argument("--icon", action="append", default=[], metavar="KEY=PATH",
                help="画像を直接指定（例: staffroll=images/sr.png）。何度でも指定可")
ap.add_argument("--track", action="append", nargs="+", default=[], metavar="ARG",
                help="曲の属性を設定: --track 曲の指定 KEY=VALUE ...（例: --track disc2:1 arrange=true）")
ap.add_argument("--export-csv", metavar="PATH", help="全曲の属性を CSV に書き出す（Excel 等で一括編集用）")
ap.add_argument("--import-csv", metavar="PATH", help="CSV の内容を曲の属性に反映する（--export-csv で作った形式）")
ap.add_argument("-i", "--interactive", action="store_true", help="対話モードで曲の属性を設定")
ap.add_argument("--csv", default="tracks.csv", metavar="PATH", help="自動で参照・書き出しする CSV（既定: tracks.csv）")
ap.add_argument("--no-csv", action="store_true", help="CSV の自動参照・書き出しをしない")
ap.add_argument("--staff", default="staff.json", metavar="PATH", help="スタッフ一覧の JSON（make_staff.py の出力。既定: staff.json。あれば config.json のスタッフより優先）")
ap.add_argument("--no-config", action="store_true", help="config.json を書き換えない（GitHub Actions など自動実行用）")
ap.add_argument("--youtube", metavar="URL", help="スタッフロールを YouTube にする（リンクか動画ID。空にすると mp4 に戻る）")
args = ap.parse_args()
root = BASE / args.audio
img_dir = BASE / args.images
story_dir = BASE / args.stories
if not root.is_dir():
    sys.exit(f"フォルダが見つかりません: {root}")

def rel(p):   # HTML から見た相対パス
    try:
        return Path(p).resolve().relative_to(BASE).as_posix()
    except ValueError:
        return Path(p).as_posix()

nfc = lambda s: unicodedata.normalize("NFC", s)

DEFAULT_CFG = {
    "album": "牛屎院風土記　〜 Unknown Chronicles of Hidden Land.",
    "default_composer": "0to784",
    "images": {"emblem": "", "cover": ""},
    "staffroll": {"label": "Staff Roll", "video": "staffroll.mp4", "youtube": "", "poster": "", "icon": "", "staff": []},
    "omake": {"label": "おまけ", "url": "https://0t0784.github.io/blog/post.html?p=2026-11-20-private-ST-01-omake", "sound": "audio/trophy.mp3",
              "title": "スタッフロール完走", "text": "左下のアイコンから「おまけ」を読めます", "icon": ""},
}

# ---------- 前回の設定（config.json → meta.json → 旧形式 audio/meta.json の順）から引き継ぐ内容を読む ----------
cfg = copy.deepcopy(DEFAULT_CFG)
disc_cfg, track_cfg = {}, {}
old_path = next((p for p in (CONFIG, META, root / "meta.json") if p.exists()), None)
if old_path:
    try:
        data = json.loads(old_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"{old_path} を読み込めません（JSONの書式エラー）: {e}")
    if old_path not in (CONFIG, META):
        print(f"旧形式の {rel(old_path)} の内容を引き継ぎます（不要になったら削除してかまいません）")
    elif old_path == META:
        print("meta.json の内容を引き継いで config.json を作ります（以後の設定は config.json に保存されます）")
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

if args.youtube is not None:                                 # --youtube URL: スタッフロールを YouTube にする（空なら mp4 に戻す）
    cfg["staffroll"]["youtube"] = args.youtube.strip()
    print("スタッフロール: " + (f"YouTube（{args.youtube.strip()}）を使います" if args.youtube.strip() else "mp4 を使います"))
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

# ---------- ストーリー(.txt)の検索 ----------
def story_for(gname, stem, idx):
    """stories/<discフォルダ名>/ から、曲のファイル名(拡張子なし)または Disc 内の曲番号(01.txt / 1.txt)に合う .txt を探す"""
    d = story_dir / gname
    if not d.is_dir():
        return ""
    files = {norm(p.stem): p for p in d.iterdir() if p.is_file() and p.suffix.lower() == ".txt"}
    for k in (stem, f"{idx:02d}", str(idx), f"track{idx:02d}"):
        if norm(k) in files:
            return rel(files[norm(k)])
    return ""

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

# ORIGINAL 系タグの名前（大文字小文字・空白・_・- は無視して比較）。名前の対応を変えたいときはここを編集
TAG_ORIG_SONG     = ("ORIGINAL", "ORIGINAL TITLE", "ORIGINAL SONG", "ORIGINALTITLE", "ORIGINALSONG")        # 原曲名
TAG_ORIG_COMPOSER = ("ORIGINAL COMPOSER", "ORIGINAL ARTIST", "ORIGINALCOMPOSER", "ORIGINALARTIST", "TOPE")  # 原作者・サークル
TAG_ORIG_WORK     = ("ORIGINAL ALBUM", "ORIGINAL WORK", "ORIGINAL GAME", "ORIGINALALBUM", "TOAL")          # 原作名

def tag_pairs(audio):
    """タグを (名前, 値) の一覧にする。mp3(ID3: TXXX・TOPE・TOAL など) / ogg・flac(Vorbis) / m4a(freeform) に対応"""
    out, tags = [], getattr(audio, "tags", None)
    if not tags:
        return out
    try:
        items = list(tags.items())
    except Exception:
        return out
    for k, v in items:
        k = str(k)
        name = k[5:] if k.startswith("TXXX:") else (k.rsplit(":", 1)[-1] if k.startswith("----:") else k)
        vals = v.text if hasattr(v, "text") else (v if isinstance(v, (list, tuple)) else [v])
        vals = [(x.decode("utf-8", "replace") if isinstance(x, bytes) else str(x)).strip() for x in vals]
        val = " / ".join(x for x in vals if x)
        if val:
            out.append((norm(name), val))
    return out

def orig_from_tags(audio):
    """ORIGINAL 系のタグから {"original": 原作者＋改行＋原作名, "original_song": 原曲名} を作る。1つも無ければ None"""
    pairs = tag_pairs(audio)
    pick = lambda names: next((v for n, v in pairs if n in {norm(x) for x in names}), "")
    song, comp, work = pick(TAG_ORIG_SONG), pick(TAG_ORIG_COMPOSER), pick(TAG_ORIG_WORK)
    if not (song or comp or work):
        return None
    original = f"{comp}\n{work}" if comp and work else (comp or work)      # 1行目: 原作者・サークル / 2行目: 原作名
    return {"original": original, "original_song": song}

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

out_discs, seen, new_tracks, auto_titles, n_story, n_tag = [], set(), 0, {}, 0, 0
for g in groups:
    tracks = []
    gname = g.name if g != root else "disc1"
    for f in sorted(g.iterdir(), key=lambda p: p.name):
        if f.suffix.lower() not in EXTS:
            continue
        a = File(f)
        if a is None or not a.info:
            print("読み込めません:", f); continue
        src = rel(f)
        key = nfc(src); seen.add(key)
        is_new = key not in track_cfg
        if not is_new:
            c = track_cfg[key]
        else:                                  # 新しい曲 → 雛形（タグにComposerがあれば初期値に）
            c = {"name": "", "composer": tag(a, ("TCOM", "composer", "\xa9wrt")) or "",
                 "arrange": False, "original": "", "original_song": ""}
            new_tracks += 1
        if is_new or args.tags:                # ORIGINAL 系のタグ → 原作・原曲・アレンジ判定
            ot = orig_from_tags(a)
            if ot:
                changed = False
                for k in ("original", "original_song"):
                    if ot[k] and c[k] != ot[k] and (args.tags == "overwrite" or not c[k]):
                        c[k] = ot[k]; changed = True
                if not c["arrange"]:
                    c["arrange"] = True; changed = True
                if changed:
                    n_tag += 1
                    print(f"  タグから反映: {f.name} → 原作: {(c['original'] or '-').replace(chr(10), ' ／ ')} / 原曲: {c['original_song'] or '-'}")
        auto = tag(a, ("TIT2", "title", "\xa9nam")) or strip_num(f.stem)
        auto_titles[src] = auto
        story = story_for(gname, f.stem, len(tracks) + 1)
        n_story += bool(story)
        tracks.append({"file": src,
                       "title": c["name"] or auto,
                       "name": c["name"],
                       "duration": round(a.info.length, 2),
                       "composer": c["composer"], "arrange": bool(c["arrange"]),
                       "original": c["original"], "original_song": c["original_song"],
                       "story": story})
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

def set_attrs(t, kv, quiet=False):
    if ("original" in kv or "original_song" in kv) and "arrange" not in kv \
            and any(kv.get(k) for k in ("original", "original_song")) and not t["arrange"]:
        kv = {**kv, "arrange": True}
        if not quiet:
            print(f"  （original/original_song が指定されたので arrange=true にしました: {t['file']}）")
    for k, v in kv.items():
        t[k] = to_bool(v) if k == "arrange" else str(v).replace("\\n", "\n")      # 文字の「\n」は改行にする（original を2行にしたいとき）
    if "name" in kv:                                           # name が空なら自動の曲名に戻る
        t["title"] = t["name"] or auto_titles.get(t["file"], t["title"])
    if not quiet:
        print("設定:", t["file"], " ", ", ".join(f"{k}={t[k]!r}" for k in kv))


# ---------- CSV で一括設定（--import-csv / --export-csv） ----------
CSV_COLS = ["file", "title_now", "name", "composer", "arrange", "original", "original_song"]   # title_now は参考用（読み込み時は無視）

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
            t = hit[0]
            before = {k: t[k] for k in ("name", "composer", "arrange", "original", "original_song")}
            set_attrs(t, kv, quiet=True); n += 1
            for k, v in before.items():            # 変わった項目だけ表示
                if t[k] != v:
                    print(f"  CSV で変更: {t['file']}  {k}: {v!r} → {t[k]!r}")
    print(f"CSV を反映しました（{n} 曲を確認）: {path}")

def export_csv(path):
    with Path(path).open("w", encoding="utf-8-sig", newline="") as fp:
        w = csv.writer(fp); w.writerow(CSV_COLS)
        for _, t in all_tracks():
            w.writerow([t["file"], t["title"], t["name"], t["composer"], "true" if t["arrange"] else "false",
                        t["original"], t["original_song"]])
    print(f"CSV を書き出しました: {path}（name 欄が空の曲は、自動の曲名が使われています）")

csv_auto = None if args.no_csv else BASE / args.csv       # 自動で参照・書き出す CSV
if args.import_csv:                                          # 明示指定: 更新日時に関係なく反映
    import_csv(args.import_csv)
elif csv_auto and csv_auto.is_file():
    ref = CONFIG if CONFIG.exists() else META                 # 比べる相手は設定ファイル（config.json。まだ無ければ meta.json）
    if not ref.exists() or csv_auto.stat().st_mtime > ref.stat().st_mtime:
        print(f"{csv_auto.name} が {ref.name} より新しいので、内容を反映します")
        import_csv(csv_auto)
    else:
        print(f"{csv_auto.name} は {ref.name} より古い（または変更なし）ので、反映せずに現在の内容で書き直します")

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
csv_written = False
if csv_auto:                                                 # 常に最新の内容で tracks.csv を書き直す（新しい曲の行も追加される）
    try:
        export_csv(csv_auto); csv_written = True
    except PermissionError:
        print(f"※ {csv_auto.name} を書き込めませんでした（Excel などで開いていませんか？ 閉じてからもう一度実行してください）")

gone = [k for k in track_cfg if k not in seen]
if gone:
    print(f"※ 音声ファイルが見つからないため設定（config.json）から削除した曲: {len(gone)} 件")
    for k in gone: print("   ", k)

# images/gif/ の GIF を名前順（数字は数として）に並べる ※ホームページ左側のスライドショー用
gif_dir = img_dir / "gif"
natural = lambda f: [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", f.name)]
gifs = [rel(f) for f in sorted(gif_dir.iterdir(), key=natural)
        if f.is_file() and f.suffix.lower() == ".gif"] if gif_dir.is_dir() else []
if gifs:
    print(f"GIFを登録: {len(gifs)}枚（{gif_dir.name}/ 内、名前順）")

# スタッフ一覧: staff.json（make_staff.py の出力）があれば、meta.json のスタッフロールにそれを使う（config.json には書き込まない）
meta_cfg = copy.deepcopy(cfg)
staff_file = BASE / args.staff
if staff_file.is_file():
    try:
        sd = json.loads(staff_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"{staff_file.name} を読み込めません（JSONの書式エラー）: {e}\n  make_staff.py をもう一度実行して作り直してください")
    lst = sd.get("staff") if isinstance(sd, dict) else sd
    if not isinstance(lst, list):
        sys.exit(f"{staff_file.name} の形式が違います（\"staff\" に一覧が入っているはずです）。make_staff.py で作り直してください")
    meta_cfg["staffroll"]["staff"] = [x for x in lst if isinstance(x, dict) and str(x.get("name", "")).strip()]
    print(f"スタッフ: {len(meta_cfg['staffroll']['staff'])}人を {staff_file.name} から読み込みました")
    yt = str(sd.get("youtube", "")).strip() if isinstance(sd, dict) else ""
    if yt and args.youtube is None:                  # --youtube を指定したときは、そちらが優先
        meta_cfg["staffroll"]["youtube"] = yt
        print(f"スタッフロール: YouTube（{yt}）を {staff_file.name} から読み込みました")
elif args.staff != "staff.json":
    sys.exit(f"スタッフ用のファイルが見つかりません: {staff_file}")

out = {"_readme": "このファイルは make_tracks.py が実行のたびに自動で作り直します（直接編集しないでください）。設定は config.json に書きます。",
       **meta_cfg, "gifs": gifs, "discs": out_discs}
META.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if not args.no_config:                                       # 設定（編集OKの項目だけ）を config.json に保存
    SET_KEYS = ("file", "name", "composer", "arrange", "original", "original_song")
    conf = {"_readme": "設定ファイル（手で編集してよい）。make_tracks.py を実行すると meta.json が作られます。書き方は make_tracks.py の冒頭を参照。",
            **cfg,
            "discs": [{"id": d["id"], "icon": d["icon"], "cover": d["cover"],
                       "tracks": [{k: t[k] for k in SET_KEYS} for t in d["tracks"]]} for d in out_discs]}
    CONFIG.write_text(json.dumps(conf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if csv_written:                                              # 次回「CSVが新しい」と誤判定しないよう、更新日時を設定ファイルに揃える
    st = (CONFIG if CONFIG.exists() else META).stat()
    os.utime(csv_auto, (st.st_atime, st.st_mtime))
print(f"ストーリー: {n_story}曲分を登録（{story_dir.name}/ 内の .txt）" if n_story else f"ストーリー: 見つかりませんでした（{story_dir.name}/disc1/track01.txt のように置くと登録されます）")
if n_tag:
    print(f"タグ(ORIGINAL系)から反映: {n_tag}曲")
print(f"meta.json を出力しました" + ("" if args.no_config else "（設定は config.json に保存）") + f"（新しい曲 {new_tracks} 曲）")
