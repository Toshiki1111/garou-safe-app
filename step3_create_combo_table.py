import sqlite3
import os

# DBファイルのパス
db_path = r"C:\dev\Garou_safe\frame_data.db"

# SQLite接続＆カーソル
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# combo_data テーブル作成（なければ）
cur.execute("""
CREATE TABLE IF NOT EXISTS combo_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character TEXT NOT NULL,
    recipe TEXT,
    advantage INTEGER NOT NULL
)
""")

# 保存＆クローズ
conn.commit()
conn.close()

print(f"コンボテーブル combo_data を作成・確認完了：{db_path}")
