import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# --- 認証（Streamlit Cloud Secrets 対応） ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "gcp_service_account" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
else:
    st.error("認証情報が見つかりません。Streamlit Secrets を設定してください。")
    st.stop()

client = gspread.authorize(creds)

# --- スプレッドシートとシート取得 ---
try:
    spreadsheet = client.open("ScoreBoard")
    sheet = spreadsheet.worksheet("予定表")
    data = sheet.get_all_values()
except Exception as e:
    st.error(f"シート読み込みに失敗しました: {e}")
    st.stop()

# --- データ整形 ---
df = pd.DataFrame(data)
df.columns = df.iloc[0]  # 1行目を列名に
df = df[1:].reset_index(drop=True)

# --- 今日の日付（列名と合わせる形式） ---
today_str = datetime.date.today().strftime("%-m/%-d")  # 例: '7/23'
if today_str not in df.columns:
    st.error(f"{today_str} のデータが見つかりません。")
    st.stop()

# --- データ抽出 ---
titles = df[df.columns[0]]       # A列：タイトル
contents = df[today_str]         # 今日の日付の列

# --- UI表示 ---
st.markdown(f"<h2 style='text-align:center;'>📅 {today_str} の予定</h2>", unsafe_allow_html=True)

# --- 授業内容（先頭 5 行） ---
st.subheader("🧑‍🏫 授業内容")
for i in range(min(5, len(df))):
    if contents[i].strip():
        st.markdown(f"- **{titles[i]}**：{contents[i]}", unsafe_allow_html=True)

# --- 課題リスト（6行目以降） ---
st.subheader("📝 課題リスト")
for i in range(5, len(df)):
    if contents[i].strip():
        st.checkbox(f"**{titles[i]}**：{contents[i]}", key=f"task_{i}")

# --- スマホ向けスペース調整 ---
st.markdown("<div style='margin-bottom:100px;'></div>", unsafe_allow_html=True)
