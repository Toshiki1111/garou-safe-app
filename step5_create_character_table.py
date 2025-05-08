import sqlite3

# DBパス
db_path = r"C:\dev\Garou_safe\frame_data.db"

# 英語⇔日本語のキャラ名対応表（添削済）
character_mapping = [
    ("B. Jenet", "B・ジェニー"),
    ("Billy", "ビリー・カーン"),
    ("CR7", "クリスティアーノ・ロナウロ"),
    ("Dong Hwan", "キム・ドンファン"),
    ("Gato", "牙刀"),
    ("Hokutomaru", "北斗丸"),
    ("Hotaru", "ほたる"),
    ("Kain", "カイン・R・ハインライン"),
    ("Kevin", "ケビン・ライアン"),
    ("Mai", "不知火舞"),
    ("Marco", "マルコ・ロドリゲス"),
    ("Preecha", "プリチャ"),
    ("Rock", "ロック・ハワード"),
    ("Salvatore", "サルヴぁトーレ・ガナッチ"),
    ("Terry", "テリー・ボガード"),
    ("Tizoc", "グリフォンマスク（ティズォック）"),
    ("Vox", "ヴォックス")
]

# DB接続
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 既存テーブルがあれば削除して作り直す
cur.execute("DROP TABLE IF EXISTS character_names")

# テーブル作成
cur.execute("""
CREATE TABLE character_names (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    english_name TEXT NOT NULL,
    japanese_name TEXT NOT NULL
)
""")

# データ投入
cur.executemany("""
INSERT INTO character_names (english_name, japanese_name)
VALUES (?, ?)
""", character_mapping)

# 保存とクローズ
conn.commit()
conn.close()

print("✅ キャラ名変換テーブル character_names を作成しました。")
