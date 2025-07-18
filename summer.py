import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# --- 認証（Streamlit Cloudでは secrets を使用） ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "gcp_service_account" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
else:
    st.error("Google Sheets の認証情報が見つかりません。secrets に gcp_service_account を設定してください。")
    st.stop()

client = gspread.authorize(creds)

# --- スプレッドシート「ScoreBoard」の「予定表」シートを取得 ---
try:
    spreadsheet = client.open("ScoreBoard")
    sheet = spreadsheet.worksheet("予定表")
    data = sheet.get_all_values()
except Exception as e:
    st.error(f"シートの読み込みに失敗しました: {e}")
    st.stop()

# --- DataFrameに変換 ---
df = pd.DataFrame(data)
df.columns = df.iloc[0]  # 1行目を列名に
df = df[1:]              # データ本体
df = df.reset_index(drop=True)

# --- 今日の日付を '7/23' のような形式で取得 ---
today_str = datetime.date.today().strftime("%-m/%-d")  # Windowsなら "%#m/%#d"

if today_str not in df.columns:
    st.error(f"本日 {today_str} の予定は見つかりません。")
    st.stop()

# --- 項目名と今日の列を取得 ---
items = df[df.columns[0]]       # 左側の「項目名」
today_col = df[today_str]       # 今日の列

# --- UI表示 ---
st.title(f"📅 {today_str} の予定")

# --- 授業予定の表示（上から5行程度） ---
st.subheader("🧑‍🏫 授業内容")
for i, (label, val) in enumerate(zip(items, today_col)):
    if i <= 4 and val.strip() != "":
        st.markdown(f"- **{label}**：{val}")

# --- 宿題一覧の表示（チェックボックス付き） ---
st.subheader("📚 宿題リスト")
for i, (label, val) in enumerate(zip(items, today_col)):
    if i > 4 and val.strip() != "":
        st.checkbox(f"{label}", key=f"hw_{i}")

# --- フッター ---
st.caption("提出状況の保存機能は未実装です。今後追加予定。")
