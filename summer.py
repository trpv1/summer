import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

# 認証情報とスプレッドシート設定
scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
credentials = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scopes
)
gc = gspread.authorize(credentials)
SPREADSHEET_KEY = "1Pv2yk28ErPUWlMevBL1F-X7y12UcfazkHZ1MyRTfB64"
worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1
data = worksheet.get_all_values()
df = pd.DataFrame(data)

# 日付取得（JST）
jst = pytz.timezone('Asia/Tokyo')
today = datetime.now(jst).strftime("%-m/%-d")
today_str = datetime.now(jst).strftime("%-m月%-d日")

# ヘッダー処理（1列目から本日列のインデックス取得）
date_row = df.iloc[0]
if today in date_row.values:
    date_index = date_row.tolist().index(today)
else:
    st.error("本日の列が見つかりません")
    st.stop()

# スローガン表示
st.title("☀️ あとで振り返ってつらかったといえる夏にしよう")

# 本日の予定
if date_row[date_index] == today:
    st.subheader(f"📅 7/{today.split('/')[-1]}（本日）の予定")
else:
    st.subheader(f"📅 {today} の予定")

# 課題リストの抽出（2〜19行目まで）
titles = df.iloc[1:19, 0].reset_index(drop=True)
times  = df.iloc[1:19, 1].reset_index(drop=True)
flags  = df.iloc[1:19, date_index].reset_index(drop=True)

# 現在時刻に基づいて進行中をハイライト
now = datetime.now(jst)
progress_index = -1
for i, t in enumerate(times):
    try:
        start_str, end_str = t.replace("〜", "-").split("-")
        start_time = datetime.strptime(start_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day, tzinfo=jst)
        end_time = datetime.strptime(end_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day, tzinfo=jst)
        if start_time <= now <= end_time:
            progress_index = i
            break
    except:
        continue

# 課題リスト表示
st.markdown("## ✅ 課題リスト")
for i in range(len(titles)):
    title = f"☑️ **{titles[i]}**"
    content = flags[i]
    if i == progress_index:
        st.success(f"{title}\n{content}")
    else:
        st.markdown(f"{title}\n{content}")

# 進捗状況バー
completed = sum(1 for c in flags if c.strip())
total = len(flags)
ratio = completed / total if total else 0
st.markdown("### 📈 課題の進捗状況")
st.progress(ratio)

# 連絡事項表示（21行目以降）
if len(df) > 21:
    notes = df.iloc[21:, date_index].dropna().tolist()
    if any(notes):
        st.subheader("📢 連絡事項")
        for note in notes:
            if note.strip():
                st.markdown(f"- {note}")
