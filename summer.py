from datetime import datetime, timedelta
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

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

@st.cache_data(ttl=300)
def load_sheet_data():
    sheet = client.open("ScoreBoard").worksheet("予定表")
    return sheet.get_all_values()

data = load_sheet_data()
df = pd.DataFrame(data)
df.columns = df.iloc[0]
df = df[1:].reset_index(drop=True)

# --- JSTの現在時刻取得 ---
now_dt = datetime.utcnow() + timedelta(hours=9)  # JST = UTC+9
if os.name == 'nt':  # Windows
    today_str = now_dt.strftime("%#m/%#d")
else:
    today_str = now_dt.strftime("%-m/%-d")

available_dates = [col for col in df.columns if col not in ["日にち", "時間"]]
default_idx = available_dates.index(today_str) if today_str in available_dates else 0
selected_date = st.selectbox("📆 表示する日付を選んでください", available_dates, index=default_idx)

titles = df["日にち"]
times = df["時間"]
contents = df[selected_date]

# --- ページ背景を白に固定 ---
st.markdown(
    """
    <style>
        body, .stApp {
            background-color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- クラススローガン ---
st.markdown(
    "<div style='text-align:center; font-size:18px; font-weight:600;'>🎯 あとで振り返って<br>つらかったといえる夏にしよう</div>",
    unsafe_allow_html=True
)

# --- タイトル ---
is_today = (selected_date == today_str)
st.markdown(
    f"<div style='text-align:center; font-size:20px; font-weight:600;'>3R3ファミリー<br>📅 {selected_date}{'（本日）' if is_today else ''} の予定</div>",
    unsafe_allow_html=True
)

# --- 進行状況バー（時間帯ごとに表示） ---
st.subheader("🛤️ 進行状況バー（時間別）")
now = now_dt.time()

for i in range(len(df)):
    title = titles[i].strip()
    time_range = times[i].strip()
    content = contents[i].strip()
    if not time_range:
        continue
    try:
        start_str, end_str = time_range.replace('〜', '-').split('-')
        start = datetime.strptime(start_str.strip(), "%H:%M").time()
        end = datetime.strptime(end_str.strip(), "%H:%M").time()
    except:
        continue

    # 状態判定とスタイル設定
    if now > end:
        style = "color: gray; opacity: 0.6;"  # 終了済み
        style_title = "color: gray; opacity: 0.6;"
        symbol = "✔️"
        border = ""
    elif start <= now <= end:
        style = "font-weight: bold; background-color: #FFD6D6; padding: 6px; border-radius: 6px;"  # 薄ピンク
        style_title = "font-weight: bold; color: #2d3436;"
        symbol = "➡️"
        border = "border: 2px solid orange;"
    else:
        style = "opacity: 1.0;"
        style_title = "color: black;"
        symbol = "○"
        border = ""

    st.markdown(
        f"""
        <div style="margin-bottom: 10px; padding: 6px; {border}">
            <span style="font-size: 18px; {style_title}">{symbol} <strong>{title}</strong></span><br>
            <span style="margin-left: 24px; {style}">{time_range}</span><br>
            <div style="margin-left: 24px; {style}">{content}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- 連絡事項 ---
st.markdown("---")
st.subheader("📢 連絡事項")
try:
    idx = df[df["日にち"] == "連絡事項"].index[0]
    ann = contents[idx].strip()
    if ann:
        st.markdown(ann)
    else:
        st.caption("（本日の連絡事項はありません）")
except IndexError:
    st.caption("（連絡事項の行が見つかりません）")

# モバイル対応の余白
st.markdown("<div style='margin-bottom:60px;'></div>", unsafe_allow_html=True)
