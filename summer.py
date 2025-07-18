import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# --- Google認証スコープ ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# --- Google Sheets認証処理 ---
if "gcp_service_account" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
else:
    st.error("認証情報がありません。Streamlit Secrets に gcp_service_account を設定してください。")
    st.stop()

client = gspread.authorize(creds)

# --- キャッシュ付き読み込み関数（5分） ---
@st.cache_data(ttl=300)
def load_sheet_data():
    spreadsheet = client.open("ScoreBoard")
    sheet = spreadsheet.worksheet("予定表")
    return sheet.get_all_values()

# --- データ取得 ---
try:
    data = load_sheet_data()
except Exception as e:
    st.error(f"スプレッドシートの読み込みに失敗しました: {e}")
    st.stop()

# --- DataFrameに変換 ---
df = pd.DataFrame(data)
df.columns = df.iloc[0]
df = df[1:].reset_index(drop=True)

# --- 今日の設定と日付選択 ---
today_str = datetime.date.today().strftime("%-m/%-d")
available_dates = [col for col in df.columns if col != df.columns[0]]
default_idx = available_dates.index(today_str) if today_str in available_dates else 0
selected_date = st.selectbox("📆 表示する日付を選んでください", available_dates, index=default_idx)

titles = df[df.columns[0]]
contents = df[selected_date]

# --- クラススローガン表示（軽量化版） ---
st.markdown(
    """
    <div style='text-align:center; font-size:18px; font-weight:600; margin-top:10px; margin-bottom:20px;'>
        🎯 あとで振り返って<br>つらかったといえる夏にしよう
    </div>
    """,
    unsafe_allow_html=True
)

# --- タイトル表示（3R3ファミリー + 本日） ---
is_today = (selected_date == today_str)
title_suffix = "（本日）" if is_today else ""
st.markdown(
    f"""
    <div style='text-align:center; font-size:20px; font-weight:600;'>
        3R3ファミリー<br>📅 {selected_date}{title_suffix} の予定
    </div>
    """,
    unsafe_allow_html=True
)

# --- 授業内容（上5行） ---
st.subheader("🧑‍🏫 授業内容")
for i in range(min(5, len(df))):
    if contents[i].strip():
        st.markdown(f"- **{titles[i]}**：{contents[i]}", unsafe_allow_html=True)

# --- 課題リスト表示 ---
st.subheader("📝 課題リスト")

task_indices = [i for i in range(5, len(df)) if contents[i].strip()]
total_tasks = len(task_indices)
completed_tasks = 0

for i in task_indices:
    title = titles[i].strip()
    content = contents[i].strip()
    key = f"{selected_date}_task_{i}"
    checked = st.checkbox(f"**{title}**：{content}", key=key)
    if checked:
        completed_tasks += 1

# --- 全体進捗表示 ---
if total_tasks > 0:
    progress = completed_tasks / total_tasks
    st.markdown("---")
    st.subheader("📈 全体の進捗状況")
    st.progress(progress)
    st.caption(f"完了：{completed_tasks} / {total_tasks} 件")
else:
    st.info("この日には課題が登録されていません。")

# --- 課題リスト表示（行インデックス 5〜19 のみ対象）---
st.subheader("📝 課題リスト")

task_indices = [i for i in range(5, 20) if contents[i].strip()]
total_tasks = len(task_indices)
completed_tasks = 0

for i in task_indices:
    title = titles[i].strip()
    content = contents[i].strip()
    key = f"{selected_date}_task_{i}"
    checked = st.checkbox(f"**{title}**：{content}", key=key)
    if checked:
        completed_tasks += 1

# --- モバイル対応：下に余白を追加 ---
st.markdown("<div style='margin-bottom:60px;'></div>", unsafe_allow_html=True)
