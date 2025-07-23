from datetime import datetime, timedelta
import os
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

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

# --- スプレッドシート読み込み（キャッシュ：5分） ---
@st.cache_data(ttl=300)
def load_sheet_data():
    sheet = client.open("ScoreBoard").worksheet("予定表")
    return sheet.get_all_values()

data = load_sheet_data()
df = pd.DataFrame(data)
df.columns = df.iloc[0]
df = df[1:].reset_index(drop=True)

# --- JST現在時刻 ---
now_dt = datetime.utcnow() + timedelta(hours=9)  # JST
if os.name == 'nt':   # Windows
    today_str = now_dt.strftime("%#m/%#d")
else:                 # macOS / Linux
    today_str = now_dt.strftime("%-m/%-d")

# --- 日付選択 ---
available_dates = [c for c in df.columns if c not in ["日にち", "時間"]]
default_idx = available_dates.index(today_str) if today_str in available_dates else 0
selected_date = st.selectbox("📆 表示する日付を選んでください", available_dates, index=default_idx)

titles   = df["日にち"]
times    = df["時間"]
contents = df[selected_date]

# --- 背景白＆文字黒 固定 ---
st.markdown("""
<style>
    body, .stApp {
        background-color: white !important;
        color: black !important;
    }

    /* ▼ selectbox 本体（表示エリア） */
    .stSelectbox > div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    /* ▼ プレースホルダー / 入力文字 */
    .stSelectbox input {
        color: #000000 !important;
    }
    /* ▼ ドロップダウンのリスト全体 */
    .stSelectbox div[role="listbox"] {
        background-color: #ffffff !important;
    }
    /* ▼ 各オプションの文字色 */
    .stSelectbox div[role="option"] {
        color: #000000 !important;
    }
    /* ▼ 矢印アイコンも黒に */
    .stSelectbox svg {
        fill: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- クラススローガン ---
st.markdown(
    "<div style='text-align:center; font-size:18px; font-weight:600;'>🎯 あとで振り返って<br>つらかったといえる夏にしよう</div>",
    unsafe_allow_html=True
)

# --- 見出し ---
is_today = (selected_date == today_str)
st.markdown(
    f"<div style='text-align:center; font-size:20px; font-weight:600;'>3R3ファミリー<br>📅 {selected_date}{'（本日）' if is_today else ''} の予定</div>",
    unsafe_allow_html=True
)

# ---------- 日付比較用ユーティリティ ----------
def md_to_date(md_str: str, base_year: int) -> datetime:
    """'7/23' 形式を同年の datetime に変換（失敗時は今日を返す）"""
    try:
        m, d = md_str.split('/')
        return datetime(base_year, int(m), int(d))
    except Exception:
        return datetime(base_year, now_dt.month, now_dt.day)

sel_date_dt  = md_to_date(selected_date, now_dt.year)
today_date_dt = md_to_date(today_str,    now_dt.year)

# ---------- 進行状況バー ----------
st.subheader("🛤️ 進行状況バー（目安）")
now_time = now_dt.time()

for i in range(len(df)):
    title      = titles[i].strip()
    time_range = times[i].strip()
    content    = contents[i].strip()

    if not time_range:
        continue

    # 時刻パース
    try:
        start_str, end_str = time_range.replace('〜', '-').split('-')
        start_t = datetime.strptime(start_str.strip(), "%H:%M").time()
        end_t   = datetime.strptime(end_str.strip(),   "%H:%M").time()
    except:
        continue

    # --- デフォルト値 ---
    opacity = "1.0"
    symbol  = "○"
    border  = ""
    bg      = "transparent"

    # 過去/今日/未来 で分岐
    if sel_date_dt < today_date_dt:
        # 過去の日付：すべて薄く＆✔️
        opacity = "0.4"
        symbol  = "✔️"
    elif sel_date_dt == today_date_dt:
        # 今日：時間帯で判定
        if now_time > end_t:
            opacity = "0.4"
            symbol  = "✔️"
        elif start_t <= now_time <= end_t:
            opacity = "1.0"
            symbol  = "➡️"
            border  = "border: 2px solid orange;"
            bg      = "#FFD6D6"  # 薄いピンク
        else:
            opacity = "1.0"
            symbol  = "○"
    else:
        # 未来：常に黒表示のまま（未経過）
        opacity = "1.0"
        symbol  = "○"

    st.markdown(
        f"""
        <div style="margin-bottom: 10px; padding: 6px; {border}; background-color: {bg}; opacity: {opacity};">
            <span style="font-size: 18px; font-weight: bold;">{symbol} <strong>{title}</strong></span><br>
            <span style="margin-left: 24px;">{time_range}</span><br>
            <div style="margin-left: 24px;">{content}</div>
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
        st.markdown(f"<div>{ann}</div>", unsafe_allow_html=True)
    else:
        st.caption("（本日の連絡事項はありません）")
except IndexError:
    st.caption("（連絡事項の行が見つかりません）")

# --- モバイル余白 ---
st.markdown("<div style='margin-bottom:60px;'></div>", unsafe_allow_html=True)
