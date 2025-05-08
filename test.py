#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
step7_display_mapping_table.py

餓狼伝説 COTW 用データベース（frame_data.db）の
character_names テーブルを一覧表示するユーティリティ。

使い方:
    python step7_display_mapping_table.py
    python step7_display_mapping_table.py --export-csv names.csv
"""

import argparse
import pathlib
import sqlite3
import sys
import pandas as pd

# ──────────────────────────────────────────────
# ■ 定数
# ──────────────────────────────────────────────
DB_PATH = pathlib.Path(r"C:\dev\Garou_safe\frame_data.db")


# ──────────────────────────────────────────────
# ■ 関数
# ──────────────────────────────────────────────
def get_character_names(db_path: pathlib.Path) -> pd.DataFrame:
    """character_names テーブルを DataFrame で取得"""
    if not db_path.exists():
        sys.exit(f"ERROR: DB が見つかりません → {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        query = """
            SELECT english_name AS English,
                   japanese_name AS Japanese
            FROM character_names
            ORDER BY Japanese
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="character_names テーブルを表示／CSV 出力します"
    )
    parser.add_argument(
        "--export-csv",
        metavar="FILE",
        help="CSV ファイルにエクスポートする（表示も行います）",
    )
    args = parser.parse_args()

    df = get_character_names(DB_PATH)

    # 表示
    print("\n=== character_names テーブル ===")
    print(df.to_string(index=False))

    # エクスポート
    if args.export_csv:
        csv_path = pathlib.Path(args.export_csv).expanduser().resolve()
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"\n✅ CSV を保存しました → {csv_path}")


# ──────────────────────────────────────────────
# ■ エントリポイント
# ──────────────────────────────────────────────
if __name__ == "__main__":
    main()
