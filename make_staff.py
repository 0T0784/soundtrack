#!/usr/bin/env python3
"""スタッフロールのスタッフ一覧と YouTube の URL を、staff.json に出力します。

■ 使い方
  1. 下の YOUTUBE にスタッフロール動画の URL、STAFF にスタッフを書く（スタッフは上から順に表示される）
  2. python make_staff.py を実行 → staff.json ができる
  3. python make_tracks.py を実行 → staff.json の内容が meta.json の「スタッフロール」に入る
     （staff.json があるときは、config.json に書いたスタッフ・YouTube より staff.json が優先される）
  ※ GitHub Pages の deploy.yml は、公開のたびに make_staff.py → make_tracks.py の順に自動で実行します。
    staff.json は自動で作られるので、リポジトリには置かず、.gitignore に「staff.json」と1行書いておくとよい。

■ YouTube の書き方（YOUTUBE）
  スタッフロール動画のリンク（watch?v= 形式 / youtu.be/ 形式 / embed・shorts・live 形式）か、動画ID（11文字）を入れる。
  ・入れると、スタッフロールのタブで mp4 の代わりに YouTube の動画が表示される（下のプレイヤーのボタンで再生・シークもできる）
  ・空（""）にすると何も出力しない → config.json の youtube、それも空なら staffroll.mp4 が使われる
  ・make_tracks.py に --youtube URL を付けて実行したときは、そちらが優先される

■ 書き方（STAFF の1人分）
  name … 名前（必須）
  role … 担当（省略可）
  text … ひとこと（省略可）。\"\"\" ～ \"\"\" の中は、そのまま改行して書ける
  icon … アイコン画像のパス（省略可）。省略したときは images/staff/ から自動で探す
         ・「01_xxx.png」のように、先頭の番号が「上から何人目か」と同じ画像
         ・または、ファイル名に name（名前）が含まれる画像
         （拡張子は png / jpg / jpeg / webp / gif / svg。見つからなければ🍂が表示される）

■ オプション
  python make_staff.py --out 別名.json        # 出力先を変える（既定: staff.json）
  python make_staff.py --icons images/other   # アイコンを自動で探すフォルダを変える（既定: images/staff）
"""
import argparse, json, re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent        # make_tracks.py と同じフォルダ

# ============================================================
# ★ スタッフロール動画の YouTube（リンクまたは動画ID。使わないときは ""）
# ============================================================
YOUTUBE = ""

# ============================================================
# ★ ここにスタッフを書く（上から順に表示される）
# ============================================================
STAFF = [
    {
        "name": "オト",
        "role": "プログラム・グラフィック・メインコンポーザー",
        "text": "知る人ぞ知る、ほどにも知られていないクリエイター",
        "icon": "images/staff/01_0to784.png",
    },
    {
        "name": "hika0906ru / koukou0906",
        "role": "ゲストコンポーザー",
        "text": """口下手で紙に絵を描くことが好きです。
好きなゲームは
星のカービィとぷよテトと
UNDERTALEとDeltaruneと
ロックマンと悪魔城ドラキュラと
ストリートファイターと色とりどりです。""",
        "icon": "images/staff/02_hika0906ru.png",
    },
    {
        "name": "ryusirou612",
        "role": "HTML完成を祈った人",
        "text": """ゲームに生活を支配されしもの。
S-BLAST92大好きマン""",
        "icon": "images/staff/03_ryusirou612.png",
    },
    {
        "name": "doufuyu",
        "role": "ストーリーシナリオを少し手伝ってくれた人",
        "text": "ぶいちゃにいます。",
        "icon": "images/staff/04_doufuyu.png",
    },
    {
        "name": "mokoyukkuri",
        "role": "ジャケットキャラクターの原案を手伝ってくれた人",
        "text": "イラスト投稿やゆっくり実況の動画投稿などしてます‼︎",
        "icon": "images/staff/05_mokoyukkuri.png",
    },
    {
        "name": "litfo",
        "role": "ジャケットキャラクターの原案を手伝ってくれた人",
        "text": "イラストを描いている韓国人の方です。",
        "icon": "images/staff/06_litfo.png",
    },
]
# ============================================================

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

ap = argparse.ArgumentParser(description="スタッフ一覧を staff.json に出力する")
ap.add_argument("--out", default="staff.json", help="出力ファイル（既定: staff.json）")
ap.add_argument("--icons", default="images/staff", help="アイコンを自動で探すフォルダ（既定: images/staff）")
args = ap.parse_args()
out_path = BASE / args.out
icon_dir = BASE / args.icons

norm = lambda s: re.sub(r"[\s_\-/]", "", s.lower())

def rel(p):   # HTML から見た相対パス
    return Path(p).resolve().relative_to(BASE).as_posix()

def find_icon(i, name):
    """icon が空のとき、icons フォルダから「i 番目の番号で始まる画像」または「名前を含む画像」を探す"""
    if not icon_dir.is_dir():
        return ""
    files = sorted(f for f in icon_dir.iterdir() if f.is_file() and f.suffix.lower() in IMG_EXTS)
    for f in files:                                   # 先頭の番号（01_xxx.png の 01）が i 番目と同じ
        m = re.match(r"0*(\d+)(?!\d)", f.stem)
        if m and int(m.group(1)) == i:
            return rel(f)
    for f in files:                                   # ファイル名に名前が含まれる
        if norm(name) and norm(name) in norm(f.stem):
            return rel(f)
    return ""

staff, problems = [], 0
for i, s in enumerate(STAFF, 1):
    name = str(s.get("name", "")).strip()
    if not name:
        print(f"※ {i}人目: name（名前）が空なので飛ばしました")
        problems += 1
        continue
    one = {"name": name}
    role, text = str(s.get("role", "")).strip(), str(s.get("text", "")).strip()
    icon = str(s.get("icon", "")).strip()
    if role: one["role"] = role
    if text: one["text"] = text
    if not icon:
        icon = find_icon(i, name)
        if icon:
            print(f"  アイコンを自動で選びました: {name} ← {icon}")
    elif not (BASE / icon).is_file():
        print(f"※ {name}: アイコンが見つかりません（{icon}）。大文字小文字・拡張子も確認してください")
        problems += 1
    if icon: one["icon"] = icon
    staff.append(one)

def yt_id(u):   # プレイヤー（HTML）と同じ読み取り方: 動画ID / youtu.be / watch?v= / embed・shorts・live・v
    u = u.strip()
    if re.fullmatch(r"[\w-]{11}", u):
        return u
    m = (re.match(r"https?://(?:[\w-]+\.)*youtu\.be/([\w-]{11})", u)
         or re.search(r"[?&]v=([\w-]{11})", u)
         or re.search(r"/(?:embed|shorts|live|v)/([\w-]{11})", u))
    return m.group(1) if m else ""

youtube = str(YOUTUBE or "").strip()
if youtube and not yt_id(youtube):
    print(f"※ YOUTUBE の URL から動画IDを読み取れません（{youtube}）。この項目は出力しません。watch?v=… 形式か youtu.be/… 形式で書いてください")
    youtube, problems = "", problems + 1

out = {"_readme": "このファイルは make_staff.py が自動で作ります（直接編集しないでください）。スタッフと YouTube は make_staff.py に書きます。"}
if youtube:
    out["youtube"] = youtube
out["staff"] = staff
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"{out_path.name} を出力しました: スタッフ {len(staff)} 人" + (f" / YouTube（動画ID: {yt_id(youtube)}）" if youtube else " / YouTube なし") + (f"（確認が必要な項目 {problems} 件）" if problems else ""))
for s in staff:
    print(f"  ・{s['name']}" + (f"  — {s['role']}" if s.get("role") else ""))
