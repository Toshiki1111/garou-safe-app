"""
step8_meaty_tool_with_low_dodge.py

変更点
--------------------------------------------------------------------
1. 「下段避け攻撃（Low Dodge Attack）」を固定枠として追加し、
   UI の列を **小ジャンプ / ジャンプ / 下段避け / 自由1 / 自由2** の 5 列に拡張
2. 下段避け攻撃の発生フレームはキャラ固定値（下の `LOW_DODGE_STARTUP`）を使用
3. 自由枠は ±0〜‑3F まで許容（早め 3F） ‑‑ 既存実装を維持
--------------------------------------------------------------------
"""

import streamlit as st
import sqlite3
import pandas as pd
from itertools import combinations

DB_PATH = r"C:\dev\Garou_safe\frame_data.db"

# ──────────────────────────────────────────────────────────────
# キャラ別 下段避け攻撃 Startup 一覧（英語名ベースに合わせる）
# ※フレーム値は画像資料から転記
# ──────────────────────────────────────────────────────────────
LOW_DODGE_STARTUP = {
    "B. Jenet": 22,
    "Billy": 24,
    "CR7": 24,
    "Dong Hwan": 24,
    "Gato": 17,           # 17F [F] と記載 → 17 とみなす
    "Hokutomaru": 23,
    "Hotaru": 23,
    "Kain": 25,
    "Kevin": 23,
    "Mai": 25,
    "Marco": 25,
    "Preecha": 24,
    "Rock": 24,
    "Salvatore": 21,
    "Terry": 26,
    "Tizoc": 26,
    "Vox": 24,
}

# ──────────────────────────────────────────────────────────────
# DB ヘルパ
# ──────────────────────────────────────────────────────────────


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_db():
    """meaty_moves に startup 列が無ければ追加"""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meaty_moves(
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            character TEXT    NOT NULL,
            move_name TEXT    NOT NULL,
            startup   INTEGER
        )
        """
    )
    cur = conn.execute("PRAGMA table_info(meaty_moves)")
    cols = [row[1] for row in cur.fetchall()]
    if "startup" not in cols:
        conn.execute("ALTER TABLE meaty_moves ADD COLUMN startup INTEGER")
    conn.commit()


@st.cache_data
def get_character_name_maps():
    conn = get_connection()
    df = pd.read_sql("SELECT english_name, japanese_name FROM character_names", conn)
    eng_to_jp = dict(zip(df["english_name"], df["japanese_name"]))
    jp_to_eng = dict(zip(df["japanese_name"], df["english_name"]))
    return eng_to_jp, jp_to_eng


@st.cache_data
def get_japanese_character_list():
    eng_to_jp, _ = get_character_name_maps()
    return sorted(eng_to_jp.values())


def get_frame_data(character, is_opponent=False):
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT name, startup, guard, hit, total,
               cancel, low_overhead
        FROM   frame_data
        WHERE  character = ?
        """,
        conn,
        params=(character,),
    )
    if is_opponent:
        df = df[df["startup"].notna() & (df["startup"] >= 1)].sort_values("startup")
    return df


def get_startup_actions(character):
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT name, startup
        FROM   frame_data
        WHERE  character = ?
          AND  startup IS NOT NULL
        """,
        conn,
        params=(character,),
    )
    return df.dropna().sort_values("startup")


def register_combo(character, recipe, advantage):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO combo_data (character, recipe, advantage)
        VALUES (?, ?, ?)
        """,
        (character, recipe, advantage),
    )
    conn.commit()


def get_combos(character):
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT recipe, advantage
        FROM   combo_data
        WHERE  character = ?
        ORDER BY id DESC
        """,
        conn,
        params=(character,),
    )
    return df


def register_meaty_move(character, move_name, startup):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO meaty_moves (character, move_name, startup)
        VALUES (?, ?, ?)
        """,
        (character, move_name, startup),
    )
    conn.commit()


def delete_meaty_moves(character, move_names):
    conn = get_connection()
    conn.executemany(
        """
        DELETE FROM meaty_moves
        WHERE  character = ?
          AND  move_name = ?
        """,
        [(character, n) for n in move_names],
    )
    conn.commit()


def get_meaty_moves(character):
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT move_name AS name, startup
        FROM   meaty_moves
        WHERE  character = ?
        """,
        conn,
        params=(character,),
    )
    return df.sort_values("startup")


def find_adjustment_moves(character, required_total, tolerance=0):
    """
    ・required_total : 追加入力で埋めたいフレーム数（正なら待ち、負なら早め）
    ・tolerance      : 早め猶予 (ex: 自由枠は -3F まで許容する → tolerance=3)
    """
    if required_total < -tolerance:
        return ["該当なし"]

    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT name, total
        FROM   frame_data
        WHERE  character = ?
          AND  total IS NOT NULL
        """,
        conn,
        params=(character,),
    )
    df = df.dropna(subset=["total"])

    # --- 単発技 ------------------------------------------------------
    singles = df[
        (df["total"] <= required_total) & (df["total"] >= required_total - tolerance)
    ]
    single_results = [
        f"{row['name']} ({int(row['total'])}F)" for _, row in singles.iterrows()
    ]

    # --- 2 技合計 ----------------------------------------------------
    pair_results = []
    for m1, m2 in combinations(df.itertuples(index=False), 2):
        ttl = m1.total + m2.total
        if required_total - tolerance <= ttl <= required_total:
            pair_results.append(
                f"{m1.name} ({int(m1.total)}F) + {m2.name} ({int(m2.total)}F)"
            )

    if not single_results and not pair_results:
        return ["該当なし"]
    return single_results + pair_results


# ──────────────────────────────────────────────────────────────
# Streamlit UI
# ──────────────────────────────────────────────────────────────
initialize_db()
st.set_page_config(layout="wide")
st.title("餓狼伝説 COTW フレーム＆コンボツール")

eng_to_jp, jp_to_eng = get_character_name_maps()
jp_names = get_japanese_character_list()

col1, col2 = st.columns(2)

# ── 左ペイン：自キャラ操作 ───────────────────────────────
with col1:
    st.header("🧍 自キャラ操作")

    default_char = st.session_state.get("selected_char", jp_names[0])
    my_jp = st.selectbox(
        "自キャラを選択", jp_names, index=jp_names.index(default_char)
    )
    st.session_state["selected_char"] = my_jp
    my_eng = jp_to_eng[my_jp]

    # --- コンボ登録 --------------------------------------------------
    st.subheader("コンボ登録")
    with st.form("combo_form"):
        recipe = st.text_input("コンボレシピ（自由記述）")
        advantage = st.number_input("有利フレーム", step=1)
        submitted = st.form_submit_button("登録する")
        if submitted and recipe:
            register_combo(my_eng, recipe, int(advantage))
            st.success("✅ コンボを登録しました！")

    # --- コンボ一覧 --------------------------------------------------
    st.subheader("登録済みコンボ")
    combos_df = get_combos(my_eng)
    st.dataframe(combos_df, use_container_width=True)

    # --- 詐欺重ね技（自由枠） --------------------------------------
    st.subheader("詐欺重ね技登録")
    startup_actions = get_startup_actions(my_eng)
    if not startup_actions.empty:
        move_to_add = st.selectbox("登録したい技", startup_actions["name"])
        if st.button("➕ 追加"):
            startup_val = int(
                startup_actions[startup_actions["name"] == move_to_add][
                    "startup"
                ].values[0]
            )
            register_meaty_move(my_eng, move_to_add, startup_val)
            st.success(f"✅ {move_to_add} を登録しました！")

    meaty_moves_df = get_meaty_moves(my_eng)
    st.markdown("##### 現在の詐欺重ね技リスト")
    st.dataframe(meaty_moves_df, use_container_width=True)

    if not meaty_moves_df.empty:
        moves_to_delete = st.multiselect(
            "🗑 削除する技を選択", meaty_moves_df["name"]
        )
        if st.button("🚮 削除"):
            delete_meaty_moves(my_eng, moves_to_delete)
            st.success("✅ 削除しました！")
            meaty_moves_df = get_meaty_moves(my_eng)

# ── 右ペイン：相手キャラ参照 ───────────────────────────────
with col2:
    st.header("🧍 相手キャラ参照")
    opp_jp = st.selectbox("相手キャラを選択", jp_names, key="opp")
    opp_eng = jp_to_eng[opp_jp]
    st.subheader("相手キャラ フレーム表（発生1F以上、昇順）")
    st.dataframe(
        get_frame_data(opp_eng, is_opponent=True), use_container_width=True
    )

# ── 詐欺重ね調整リスト ──────────────────────────────────
st.divider()
st.subheader("🎯 詐欺重ね調整リスト（自由枠付き）")

# 基本データ（自由枠候補）
startup_actions_full = get_startup_actions(my_eng)
meaty_moves_df = get_meaty_moves(my_eng)
base_df = (
    meaty_moves_df if not meaty_moves_df.empty else startup_actions_full
)
names = base_df["name"].tolist()

if names:
    default_action1 = st.session_state.get("selected_action_1", names[0])
    default_action2 = st.session_state.get(
        "selected_action_2", names[1] if len(names) > 1 else names[0]
    )
else:
    default_action1 = default_action2 = ""

# 下段避け攻撃の startup を取得
low_dodge_startup = LOW_DODGE_STARTUP.get(my_eng)
if low_dodge_startup is None:
    st.error(f"⚠ 下段避け攻撃の発生値が未登録: {my_eng}")
    low_dodge_startup = 0

# 5 列レイアウト
colA, colB, colC, colD, colE = st.columns(5)

with colA:
    st.markdown("### 🕊 小ジャンプ（+34F）")

with colB:
    st.markdown("### 🕊 ジャンプ（+41F）")

with colC:
    st.markdown(f"### 🛡 下段避け攻撃（{low_dodge_startup}F）")

with colD:
    if names:
        idx1 = names.index(default_action1) if default_action1 in names else 0
        action1 = st.selectbox("🔧 自由選択1", names, index=idx1, key="action1")
        startup1 = int(base_df[base_df["name"] == action1]["startup"].values[0])
        st.session_state["selected_action_1"] = action1
        st.markdown(f"### 🕊 {action1}（{startup1}F）")
    else:
        startup1 = 0
        st.markdown("### ---")

with colE:
    if names:
        idx2 = names.index(default_action2) if default_action2 in names else 0
        action2 = st.selectbox("🔧 自由選択2", names, index=idx2, key="action2")
        startup2 = int(base_df[base_df["name"] == action2]["startup"].values[0])
        st.session_state["selected_action_2"] = action2
        st.markdown(f"### 🕊 {action2}（{startup2}F）")
    else:
        startup2 = 0
        st.markdown("### ---")

# ── 各コンボに対する調整リスト -----------------------------------
for _, row in combos_df.iterrows():
    adv = row["advantage"]
    recipe = row["recipe"]

    colA, colB, colC, colD, colE = st.columns(5)

    with colA:
        st.markdown(f"**{recipe}（+{adv}F） → 小ジャンプ**")
        required = adv - 34
        for r in find_adjustment_moves(my_eng, required, tolerance=0):
            st.write("- " + r)

    with colB:
        st.markdown(f"**{recipe}（+{adv}F） → ジャンプ**")
        required = adv - 41
        for r in find_adjustment_moves(my_eng, required, tolerance=0):
            st.write("- " + r)

    with colC:
        st.markdown(f"**{recipe}（+{adv}F） → 下段避け攻撃**")
        required = adv - low_dodge_startup
        for r in find_adjustment_moves(my_eng, required, tolerance=0):
            st.write("- " + r)

    with colD:
        st.markdown(f"**{recipe}（+{adv}F） → {action1}**")
        required = adv - startup1
        for r in find_adjustment_moves(my_eng, required, tolerance=3):
            st.write("- " + r)

    with colE:
        st.markdown(f"**{recipe}（+{adv}F） → {action2}**")
        required = adv - startup2
        for r in find_adjustment_moves(my_eng, required, tolerance=3):
            st.write("- " + r)

# ── 自キャラフレーム表 ──────────────────────────────────
st.divider()
st.subheader("📋 自キャラ フレーム表")
st.dataframe(get_frame_data(my_eng), use_container_width=True)
