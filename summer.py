import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# --- 認証 ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# --- シート取得 ---
spreadsheet = client.open("ScoreBoard")
sheet = spreadsheet.worksheet("予定表")  # 第4シート（名前で指定）

# --- データ読み込み ---
data = sheet.get_all_values()
df = pd.DataFrame(data)

# --- ヘッダーと日付列の処理 ---
df.columns = df.iloc[0]  # 1行目を列名に
df = df[1:]              # データ本体
df = df.reset_index(drop=True)

# --- 今日の列（日付文字列）を取得 ---
today_str = datetime.date.today().strftime("%-m/%-d")  # 例: '7/23'

if today_str not in df.columns:
    st.error(f"本日 {today_str} の予定は登録されていません。")
    st.stop()

# --- 項目名列を取得（A列） ---
items = df[df.columns[0]]  # 「日程項目」列（1列目）

# --- 今日の列の内容を取得 ---
today_col = df[today_str]

# --- 表示 ---
st.title(f"📅 {today_str} の予定")

# --- 授業表示（2行目〜5行目あたり） ---
st.subheader("授業内容")
for i, (label, val) in enumerate(zip(items, today_col)):
    if i <= 4 and val.strip() != "":
        st.write(f"● {label}：{val}")

# --- 宿題表示（6行目以降） ---
st.subheader("宿題一覧")
for i, (label, val) in enumerate(zip(items, today_col)):
    if i > 4 and val.strip() != "":
        st.checkbox(f"{label}", key=f"hw_{i}")
