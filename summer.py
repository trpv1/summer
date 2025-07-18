import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# --- 認証 ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "gcp_service_account" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
else:
    st.error("認証情報が設定されていません。Streamlit Secrets に gcp_service_account を登録してください。")
    st.stop()

client = gspread.authorize(creds)

# --- シート取得 ---
try:
    spreadsheet = client.open("ScoreBoard")
    sheet = spreadsheet.worksheet("予定表")
    data = sheet.get_all_values()
except Exception as e:
    st.error(f"スプレッドシートの読み込みに失敗しました: {e}")
    st.stop()

# --- DataFrameに変換 ---
df = pd.DataFrame(data)
df.columns = df.iloc[0]  # 1行目を列名に（例: 7/23, 7/24...）
df = df[1:].reset_index(drop=True)

# --- 日付選択（デフォルトは今日） ---
today_str = datetime.date.today().strftime("%-m/%-d")  # 例: '7/24'
available_dates = [col for col in df.columns if col != df.columns[0]]

if today_str in available_dates:
    default_idx = available_dates.index(today_str)
else:
    default_idx = 0

selected_date = st.selectbox("📆 表示する日付を選んでください", available_dates, index=default_idx)

# --- データ取り出し ---
titles = df[df.columns[0]]         # 一番左の列（課題名・見出しなど）
contents = df[selected_date]       # 選択された日付列

# --- クラススローガン ---
st.markdown(
    """
    <div style='text-align: center; font-size: 20px; font-weight: bold; margin-top: 10px; margin-bottom: 30px;'>
        🎯 あとで振り返って<br>
        つらかったといえる夏にしよう
    </div>
    """,
    unsafe_allow_html=True
)

# --- ヘッダー表示 ---
st.markdown(f"<h2 style='text-align:center;'>📅 {selected_date} の予定</h2>", unsafe_allow_html=True)

# --- 授業内容（上5行程度） ---
st.subheader("🧑‍🏫 授業内容")
for i in range(min(5, len(df))):
    if contents[i].strip():
        st.markdown(f"- **{titles[i]}**：{contents[i]}", unsafe_allow_html=True)

# --- 課題リスト（課題：内容、チェック付き） ---
st.subheader("📝 課題リスト")
total_students = 10  # 仮の合計人数（今後Google Sheets集計に置き換え）

for i in range(5, len(df)):
    title = titles[i].strip()
    content = contents[i].strip()
    if content:
        key = f"{selected_date}_task_{i}"
        checked = st.checkbox(f"**{title}**：{content}", key=key)
        # 仮の提出人数：チェックされたら1人とカウント
        submitted = 1 if checked else 0
        st.progress(submitted / total_students)
        st.caption(f"提出状況：{submitted} / {total_students}")

# --- フッター余白 ---
st.markdown("<div style='margin-bottom: 100px;'></div>", unsafe_allow_html=True)
