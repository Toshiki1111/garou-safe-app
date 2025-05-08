import streamlit as st
import sqlite3
import pandas as pd
from itertools import combinations

DB_PATH = r"frame_data.db"

LOW_DODGE_STARTUP = {
    "B. Jenet": 22, "Billy": 24, "CR7": 24, "Dong Hwan": 24,
    "Gato": 17, "Hokutomaru": 23, "Hotaru": 23, "Kain": 25,
    "Kevin": 23, "Mai": 25, "Marco": 25, "Preecha": 24,
    "Rock": 24, "Salvatore": 21, "Terry": 26, "Tizoc": 26, "Vox": 24,
}

LATE_TOLERANCE = 2


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meaty_moves(
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            character TEXT NOT NULL,
            move_name TEXT NOT NULL,
            startup   INTEGER
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS combo_data(
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            character TEXT NOT NULL,
            recipe    TEXT NOT NULL,
            advantage INTEGER NOT NULL
        )
        """
    )
    cur = conn.execute("PRAGMA table_info(meaty_moves)")
    if "startup" not in [row[1] for row in cur.fetchall()]:
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
        SELECT name, startup, guard, hit, total, cancel, low_overhead
        FROM frame_data WHERE character = ?
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
        FROM frame_data
        WHERE character = ? AND startup IS NOT NULL
        """,
        conn,
        params=(character,),
    )
    return df.dropna().sort_values("startup")


def register_combo(character, recipe, advantage):
    conn = get_connection()
    conn.execute(
        "INSERT INTO combo_data (character, recipe, advantage) VALUES (?, ?, ?)",
        (character, recipe, advantage),
    )
    conn.commit()


def update_combo(combo_id, new_recipe, new_advantage):
    conn = get_connection()
    conn.execute(
        "UPDATE combo_data SET recipe = ?, advantage = ? WHERE id = ?",
        (new_recipe, new_advantage, combo_id),
    )
    conn.commit()


def delete_combo(combo_id):
    conn = get_connection()
    conn.execute("DELETE FROM combo_data WHERE id = ?", (combo_id,))
    conn.commit()


def get_combos(character):
    conn = get_connection()
    return pd.read_sql(
        "SELECT id, recipe, advantage FROM combo_data WHERE character = ? ORDER BY id DESC",
        conn,
        params=(character,),
    )


def register_meaty_move(character, move_name, startup):
    conn = get_connection()
    conn.execute(
        "INSERT INTO meaty_moves (character, move_name, startup) VALUES (?, ?, ?)",
        (character, move_name, startup),
    )
    conn.commit()


def delete_meaty_moves(character, move_names):
    conn = get_connection()
    conn.executemany(
        "DELETE FROM meaty_moves WHERE character = ? AND move_name = ?",
        [(character, n) for n in move_names],
    )
    conn.commit()


def get_meaty_moves(character):
    conn = get_connection()
    return pd.read_sql(
        "SELECT move_name AS name, startup FROM meaty_moves WHERE character = ?",
        conn,
        params=(character,),
    ).sort_values("startup")


def _format_result(desc: str, total: int, required: int) -> str:
    diff = total - required
    return f"{desc} ({total}F)(+{diff}F)"


def find_adjustment_moves(character: str, required_total: int, tolerance_plus: int = 0):
    if required_total < 0:
        return ["該当なし"]

    conn = get_connection()
    df = pd.read_sql(
        "SELECT name, total FROM frame_data WHERE character = ? AND total IS NOT NULL",
        conn,
        params=(character,),
    ).dropna(subset=["total"])

    min_total, max_total = required_total, required_total + tolerance_plus

    singles = df[(df["total"] >= min_total) & (df["total"] <= max_total)]
    single_results = [
        _format_result(row["name"], int(row["total"]), required_total)
        for _, row in singles.iterrows()
    ]

    pair_results = []
    for m1, m2 in combinations(df.itertuples(index=False), 2):
        ttl = m1.total + m2.total
        if min_total <= ttl <= max_total:
            pair_results.append(
                _format_result(
                    f"{m1.name} ({int(m1.total)}F) + {m2.name} ({int(m2.total)}F)",
                    ttl,
                    required_total,
                )
            )

    return single_results + pair_results if single_results or pair_results else ["該当なし"]


initialize_db()
st.set_page_config(layout="wide")
st.title("餓狼伝説 COTW フレーム＆コンボツール")

eng_to_jp, jp_to_eng = get_character_name_maps()
jp_names = get_japanese_character_list()

col1, col2 = st.columns(2)

with col1:
    st.header("🧍 自キャラ操作")

    default_char = st.session_state.get("selected_char", jp_names[0])
    my_jp = st.selectbox("自キャラを選択", jp_names, index=jp_names.index(default_char))
    st.session_state["selected_char"] = my_jp
    my_eng = jp_to_eng[my_jp]

    st.subheader("コンボ登録")
    with st.form("combo_form"):
        recipe = st.text_input("コンボレシピ（自由記述）")
        advantage = st.number_input("有利フレーム", step=1)
        if st.form_submit_button("登録する") and recipe:
            register_combo(my_eng, recipe, int(advantage))
            st.success("✅ コンボを登録しました！")

    st.subheader("登録済みコンボ")
    combos_df = get_combos(my_eng)
    st.dataframe(combos_df[["recipe", "advantage"]], use_container_width=True)

    st.markdown("#### コンボ修正 / 削除")
    if not combos_df.empty:
        combo_opts = combos_df.apply(
            lambda r: f"{r['id']}: {r['recipe']} (+{r['advantage']}F)", axis=1
        ).tolist()
        sel = st.selectbox("編集するコンボ", combo_opts, key="combo_edit_sel")
        sel_id = int(sel.split(":")[0])
        sel_row = combos_df[combos_df["id"] == sel_id].iloc[0]

        new_recipe = st.text_input("レシピ", sel_row["recipe"], key="edit_recipe")
        new_adv = st.number_input(
            "有利F", step=1, value=int(sel_row["advantage"]), key="edit_adv"
        )

        col_u, col_d = st.columns(2)
        with col_u:
            if st.button("💾 更新", key="update_btn"):
                update_combo(sel_id, new_recipe, int(new_adv))
                st.success("✅ 更新しました！")
                st.experimental_rerun()
        with col_d:
            if st.button("🗑 削除", key="delete_btn"):
                delete_combo(sel_id)
                st.success("✅ 削除しました！")
                st.experimental_rerun()
    else:
        st.info("コンボが登録されていません。")

    st.subheader("詐欺重ね技登録（自由枠候補）")
    startup_actions = get_startup_actions(my_eng)
    if not startup_actions.empty:
        move_to_add = st.selectbox("登録したい技", startup_actions["name"])
        if st.button("➕ 追加"):
            startup_val = int(
                startup_actions[startup_actions["name"] == move_to_add]["startup"].values[0]
            )
            register_meaty_move(my_eng, move_to_add, startup_val)
            st.success(f"✅ {move_to_add} を登録しました！")
            st.experimental_rerun()

    meaty_moves_df = get_meaty_moves(my_eng)
    st.markdown("##### 現在の詐欺重ね技リスト")
    st.dataframe(meaty_moves_df, use_container_width=True)

    if not meaty_moves_df.empty:
        moves_to_delete = st.multiselect("🗑 削除する技を選択", meaty_moves_df["name"])
        if st.button("🚮 削除"):
            delete_meaty_moves(my_eng, moves_to_delete)
            st.success("✅ 削除しました！")
            st.experimental_rerun()

with col2:
    st.header("🧍 相手キャラ参照")
    opp_jp = st.selectbox("相手キャラを選択", jp_names, key="opp")
    opp_eng = jp_to_eng[opp_jp]
    st.subheader("相手キャラ フレーム表（発生1F以上、昇順）")
    st.dataframe(get_frame_data(opp_eng, is_opponent=True), use_container_width=True)

st.divider()
st.subheader("🎯 詐欺重ね調整リスト（自由枠は 0〜+2F 許容）")

base_df = meaty_moves_df if not meaty_moves_df.empty else startup_actions
names = base_df["name"].tolist()

default_action1 = st.session_state.get("selected_action_1", names[0] if names else "")
default_action2 = st.session_state.get(
    "selected_action_2", names[1] if len(names) > 1 else default_action1
)

low_dodge_startup = LOW_DODGE_STARTUP.get(my_eng, 0)

colA, colB, colC, colD, colE = st.columns(5)

with colA:
    st.markdown("### 🕊 小ジャンプ（+34F） (±0F)")

with colB:
    st.markdown("### 🕊 ジャンプ（+41F） (±0F)")

with colC:
    st.markdown(f"### 🛡 下段避け攻撃（{low_dodge_startup}F） (±0F)")

with colD:
    if names:
        idx1 = names.index(default_action1) if default_action1 in names else 0
        action1 = st.selectbox("🔧 自由選択1", names, index=idx1, key="action1")
        startup1 = int(base_df[base_df["name"] == action1]["startup"].values[0])
        st.session_state["selected_action_1"] = action1
        st.markdown(f"### 🕊 {action1}（{startup1}F） (0〜+2F)")
    else:
        startup1 = 0
        st.markdown("### ---")

with colE:
    if names:
        idx2 = names.index(default_action2) if default_action2 in names else 0
        action2 = st.selectbox("🔧 自由選択2", names, index=idx2, key="action2")
        startup2 = int(base_df[base_df["name"] == action2]["startup"].values[0])
        st.session_state["selected_action_2"] = action2
        st.markdown(f"### 🕊 {action2}（{startup2}F） (0〜+2F)")
    else:
        startup2 = 0
        st.markdown("### ---")

for _, row in combos_df.iterrows():
    adv = row["advantage"]
    recipe = row["recipe"]

    colA, colB, colC, colD, colE = st.columns(5)

    with colA:
        st.markdown(f"**{recipe}（+{adv}F） → 小ジャンプ**")
        required = adv - 34
        for r in find_adjustment_moves(my_eng, required):
            st.write("- " + r)

    with colB:
        st.markdown(f"**{recipe}（+{adv}F） → ジャンプ**")
        required = adv - 41
        for r in find_adjustment_moves(my_eng, required):
            st.write("- " + r)

    with colC:
        st.markdown(f"**{recipe}（+{adv}F） → 下段避け攻撃**")
        required = adv - low_dodge_startup
        for r in find_adjustment_moves(my_eng, required):
            st.write("- " + r)

    with colD:
        st.markdown(f"**{recipe}（+{adv}F） → {action1}**")
        required = adv - startup1
        for r in find_adjustment_moves(my_eng, required, tolerance_plus=LATE_TOLERANCE):
            st.write("- " + r)

    with colE:
        st.markdown(f"**{recipe}（+{adv}F） → {action2}**")
        required = adv - startup2
        for r in find_adjustment_moves(my_eng, required, tolerance_plus=LATE_TOLERANCE):
            st.write("- " + r)

st.divider()
st.subheader("📋 自キャラ フレーム表")
st.dataframe(get_frame_data(my_eng), use_container_width=True)
