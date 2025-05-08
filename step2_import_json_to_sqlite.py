import json
import sqlite3
import os

# JSONファイルとDBのパス設定
json_path = r"C:\dev\Garou_safe\json\garou_frame_data.json"
db_path = r"C:\dev\Garou_safe\frame_data.db"

# JSON読み込み
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# SQLite接続＆カーソル取得
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 既存テーブル削除（再投入用）
cur.execute("DROP TABLE IF EXISTS frame_data")

# テーブル作成
cur.execute("""
CREATE TABLE frame_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character TEXT,
    name TEXT,
    startup INTEGER,
    guard TEXT,
    hit TEXT,
    total INTEGER,
    cancel TEXT,
    low_overhead TEXT
)
""")

# データ投入
for char_entry in data:
    character = char_entry["character"]
    for move in char_entry["moves"]:
        cur.execute("""
        INSERT INTO frame_data (
            character, name, startup, guard, hit, total, cancel, low_overhead
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character,
            move.get("name"),
            move.get("startup"),
            move.get("guard"),
            move.get("hit"),
            move.get("total"),
            move.get("cancel"),
            move.get("low_overhead")
        ))

# コミット＆クローズ
conn.commit()
conn.close()

print(f"SQLite DB作成・データ投入完了：{db_path}")
