import pandas as pd
import json
import os
import re

# パス設定
excel_path = r"C:\dev\Garou_safe\Fatal Fury_ City of the Wolves Frame Data by Juicebox.xlsx"
json_output_dir = r"C:\dev\Garou_safe\json"
json_output_path = os.path.join(json_output_dir, "garou_frame_data.json")

# Excel読み込み
xls = pd.ExcelFile(excel_path)

# 対象キャラシート
character_sheets = [s for s in xls.sheet_names if s in [
    'B. Jenet', 'Billy', 'CR7', 'Dong Hwan', 'Gato', 'Hokutomaru',
    'Hotaru', 'Kain', 'Kevin', 'Mai', 'Marco', 'Preecha',
    'Rock', 'Salvatore', 'Terry', 'Tizoc', 'Vox'
]]

# 技名変換関数
def convert_name(name):
    if not isinstance(name, str):
        return name
    name = re.sub(r'(?i)\bclose\b', '近', name)
    name = re.sub(r'(?i)\bair\b', '空中', name)
    name = re.sub(r'(?i)\bc\+d\b', 'REVブロウ', name)
    return name

# Low/Overhead列の変換関数
def convert_low_overhead(value):
    if pd.isna(value):
        return "なし"
    value_str = str(value).strip().lower()
    if value_str == "//":
        return "上段"
    elif value_str == "low":
        return "下段"
    elif value_str == "overhead":
        return "中段"
    else:
        return "なし"

# 全キャラデータ収集
all_data = []

for sheet in character_sheets:
    df = xls.parse(sheet)

    # ターゲットコンボ（>）除去
    df = df[~df["Unnamed: 0"].astype(str).str.startswith(">")]

    # 列名標準化
    df = df.rename(columns={
        "Unnamed: 0": "name",
        "Start": "startup",
        "Guard": "guard",
        "Hit": "hit",
        "Total": "total",
        "Cancel": "cancel",
        "Low/Overhead": "low_overhead"
    })

    # 技名・属性変換
    df["name"] = df["name"].apply(convert_name)
    df["low_overhead"] = df["low_overhead"].apply(convert_low_overhead)

    # 数値変換
    def to_int(val):
        try:
            return int(val)
        except:
            return None

    df["startup"] = df["startup"].apply(to_int)
    df["total"] = df["total"].apply(to_int)

    # 有効データのみ抽出
    character_data = {
        "character": sheet,
        "moves": df[["name", "startup", "guard", "hit", "total", "cancel", "low_overhead"]]
        .dropna(subset=["name"])
        .to_dict(orient="records")
    }

    all_data.append(character_data)

# 出力フォルダがなければ作成
os.makedirs(json_output_dir, exist_ok=True)

# JSON出力
with open(json_output_path, "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print(f"JSONファイルを保存しました：{json_output_path}")
