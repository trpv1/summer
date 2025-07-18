import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# --- 認証設定 ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "gcp_service_account" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
else:
    st.error("認証情報が設定されていません。Streamlit Secrets に gcp_service_account を登録してください。")
    st.stop()

client = gspread.authorize(creds)

# --- スプレッドシート読み込み ---
try:
    spreadsheet = client.open("ScoreBoard")
    sheet = spreadsheet.worksheet("予定表")
    data = sheet.get_all_values()
except Exception as e:
    st.error(f"スプレッドシートの読み込みに失敗しました: {e}")
    st.stop()

# --- DataFrame化と整形 ---
df = pd.DataFrame(data)
df.columns = df.iloc[0]
df = df[1:].reset_index(drop=True)

# --- 今日の文字列と日付選択 ---
today_str = datetime.date.today().strftime("%-m/%-d")  # 例: '7/18'
available_dates = [col for col in df.columns if col != df.columns[0]]

default_idx = available_dates.index(today_str) if today_str in available_dates else 0
selected_date = st.selectbox("📆 表示する日付を選んでください", available_dates, index=default_idx)

# --- データ抽出 ---
titles = df[df.columns[0]]         # 左端列
contents = df[selected_date]       # 選択された日付の列

# --- スローガン表示 ---
st.markdown(
    """
    <div style='text-align: center; font-size: 20px; font-weight: bold; margin-top: 10px; margin-bottom: 30px;'>
        🎯 あとで振り返って<br>
        つらかったといえる夏にしよう
    </div>
    """,
    unsafe_allow_html=True
)

# --- タイトル表示 ---
is_today = (selected_date == today_str)
title_suffix = "（本日）" if is_today else ""
st.markdown(
    f"<h2 style='text-align:center;'>📅 {selected_date}{title_suffix} の予定</h2>",
    unsafe_allow_html=True
)

# --- 授業内容表示（上5行） ---
st.subheader("🧑‍🏫 授業内容")
for i in range(min(5, len(df))):
    if contents[i].strip():
        st.markdown(f"- **{titles[i]}**：{contents[i]}", unsafe_allow_html=True)

# --- 課題リスト表示と進捗管理 ---
st.subheader("📝 課題リスト")

task_indices = []
for i in range(5, len(df)):
    if contents[i].strip():
        task_indices.append(i)

total_tasks = len(task_indices)
completed_tasks = 0

for i in task_indices:
    title = titles[i].strip()
    content = contents[i].strip()
    key = f"{selected_date}_task_{i}"
    checked = st.checkbox(f"**{title}**：{content}", key=key)
    if checked:
        completed_tasks += 1

# --- 全体進捗バー表示 ---
if total_tasks > 0:
    progress = completed_tasks / total_tasks
    st.markdown("---")
    st.subheader("📈 全体の進捗状況")
    st.progress(progress)
    st.caption(f"完了：{completed_tasks} / {total_tasks} 件")
else:
    st.info("この日には課題が登録されていません。")

# --- スマホ向け余白 ---
st.markdown("<div style='margin-bottom: 80px;'></div>", unsafe_allow_html=True)
