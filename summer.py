"""
大きなスケジュールボード (デモ用 1 分刻み)
========================================
Streamlit v1.33 互換：自動リロードは `time.sleep(1)` → `st.experimental_rerun()` に変更。

* **開始時刻 10:25**、以降 1 分刻みで 11 セッションを設定し動作確認が容易
* Google Sheets 依存なし
* iPad 横持ちで遠くから読める高コントラスト UI

起動：
```bash
streamlit run big_schedule_board.py
```

停止したい場合は Streamlit サーバを `Ctrl + C` で終了してください。
"""

from __future__ import annotations

import time as _time
from datetime import datetime, time, timedelta
from typing import List, Tuple

import streamlit as st

# -----------------------------------------------------------------------------
# ページ設定
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="3R3 スケジュールボード デモ",
    page_icon="🕒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# タイムテーブル（JST） 10:25 から 1 分刻み
# -----------------------------------------------------------------------------
SCHEDULE: List[Tuple[str, str, str]] = [
    ("10:25", "10:26", "授業前"),
    ("10:26", "10:27", "テスト開始5分前カウントダウン"),
    ("10:27", "10:28", "テスト開始"),
    ("10:28", "10:29", "テスト終了5分前カウントダウン"),
    ("10:29", "10:30", "テスト終了採点"),
    ("10:30", "10:31", "とことん演習開始"),
    ("10:31", "10:32", "とことん演習終了5分前カウントダウン"),
    ("10:32", "10:33", "休憩時間"),
    ("10:33", "10:34", "休憩終了5分前カウントダウン"),
    ("10:34", "10:35", "授業開始"),
    ("10:35", "10:36", "授業終了10分前カウントダウン"),
]

# -----------------------------------------------------------------------------
# スタイル (CSS)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        body, .stApp { background:#ffffff !important; color:#000000 !important; }
        /* 中央のメイン表示 */
        .now-block {
            border-radius: 24px;
            padding: 40px 20px;
            background:#ffebee;
            border: 4px solid #e53935;
            text-align:center;
            margin-bottom:40px;
            box-shadow:0 4px 12px rgba(0,0,0,0.15);
        }
        .now-time { font-size: 64px; font-weight: 800; }
        .now-title { font-size: 56px; font-weight: 800; margin-top:20px; }
        .now-span { font-size: 32px; margin-top:12px; }

        /* 次の予定 */
        .next-block {
            border-radius: 16px;
            padding: 20px;
            background:#e3f2fd;
            border: 3px solid #1e88e5;
            text-align:center;
            box-shadow:0 2px 8px rgba(0,0,0,0.1);
        }
        .next-title { font-size: 36px; font-weight:700; }
        .next-time  { font-size: 28px; margin-top:8px; }

        /* 過去・未来のリスト */
        .schedule-table { width:100%; border-collapse:collapse; margin-top:40px; }
        .schedule-table td { padding:12px 8px; font-size:24px; }
        .schedule-past  { color:#9e9e9e; text-decoration:line-through; }
        .schedule-now   { background:#fff3e0; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# ユーティリティ
# -----------------------------------------------------------------------------
JST = datetime.utcnow() + timedelta(hours=9)


def str_to_time(hm: str) -> time:
    return datetime.strptime(hm, "%H:%M").time()


# 現在のセッションと次のセッションを決定
now_event = None
next_event = None
for start, end, label in SCHEDULE:
    start_t, end_t = str_to_time(start), str_to_time(end)
    if start_t <= JST.time() <= end_t:
        now_event = (start, end, label)
    elif JST.time() < start_t and next_event is None:
        next_event = (start, end, label)

# -----------------------------------------------------------------------------
# 中央メイン表示
# -----------------------------------------------------------------------------
if now_event:
    start, end, title = now_event
    end_dt = datetime.combine(JST.date(), str_to_time(end))
    remaining = end_dt - JST
    remaining_str = str(remaining).split(".")[0]  # hh:mm:ss
    st.markdown(
        f"""
        <div class="now-block">
            <div class="now-time">{JST.strftime('%H:%M:%S')}</div>
            <div class="now-title">{title}</div>
            <div class="now-span">終了まで {remaining_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div class="now-block" style="background:#e0f2f1; border-color:#00897b;">
            <div class="now-time">{JST.strftime('%H:%M:%S')}</div>
            <div class="now-title">スケジュール外</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# 次の予定
# -----------------------------------------------------------------------------
if next_event:
    n_start, n_end, n_title = next_event
    start_dt = datetime.combine(JST.date(), str_to_time(n_start))
    until_next = start_dt - JST
    until_next_str = str(until_next).split(".")[0]

    st.markdown(
        f"""
        <div class="next-block">
            <div class="next-title">次: {n_title}</div>
            <div class="next-time">{n_start} – {n_end} (開始まで {until_next_str})</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# 全スケジュール一覧
# -----------------------------------------------------------------------------
st.markdown("### 📋 本日のタイムテーブル (1 分刻みデモ)")

rows = []
for start, end, label in SCHEDULE:
    start_t, end_t = str_to_time(start), str_to_time(end)
    cls = ""
    if JST.time() > end_t:
        cls = "schedule-past"
    elif start_t <= JST.time() <= end_t:
        cls = "schedule-now"

    rows.append(f"<tr class='{cls}'><td>{start} – {end}</td><td>{label}</td></tr>")

st.markdown(
    f"""
    <table class="schedule-table">
        {''.join(rows)}
    </table>
    """,
    unsafe_allow_html=True,
)

# 末尾余白
st.markdown("<div style='margin-bottom:60px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 自動リロード：1 秒待って再実行
# -----------------------------------------------------------------------------
_time.sleep(1)
st.experimental_rerun()
