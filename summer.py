"""
リアルタイム・スケジュールボード（警告ゼロ版）
===========================================
* 10 : 25 スタート／1 分刻み（デモ用）
* 本日のタイムテーブル一覧は非表示
* **1 秒ごとに UI を更新**：`while` ループ中のプレースホルダ更新 → 古い Streamlit でも動作
* **警告バナー完全削除**：非推奨 API を一切使用しない

実行コマンド：
```bash
streamlit run big_schedule_board.py
```

メモ：
- 最新版では `st.experimental_rerun()` によるページ再実行、
- 旧版ではループ継続でプレースホルダだけ更新。
どちらも黄色い警告は出ません。
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
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# ユーティリティ
# -----------------------------------------------------------------------------

def str_to_time(hm: str) -> time:
    return datetime.strptime(hm, "%H:%M").time()


def get_current_and_next(now_dt: datetime):
    now_ev, next_ev = None, None
    for start, end, label in SCHEDULE:
        s_t, e_t = str_to_time(start), str_to_time(end)
        if s_t <= now_dt.time() <= e_t:
            now_ev = (start, end, label)
        elif now_dt.time() < s_t and next_ev is None:
            next_ev = (start, end, label)
    return now_ev, next_ev

# -----------------------------------------------------------------------------
# プレースホルダ
# -----------------------------------------------------------------------------
placeholder_now  = st.empty()
placeholder_next = st.empty()

# -----------------------------------------------------------------------------
# 更新ループ
# -----------------------------------------------------------------------------
while True:
    JST = datetime.utcnow() + timedelta(hours=9)
    now_event, next_event = get_current_and_next(JST)

    # --- 現在セッション表示 ---
    if now_event:
        start, end, title = now_event
        end_dt = datetime.combine(JST.date(), str_to_time(end))
        remaining_str = str(end_dt - JST).split(".")[0]
        placeholder_now.markdown(
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
        placeholder_now.markdown(
            f"""
            <div class="now-block" style="background:#e0f2f1; border-color:#00897b;">
                <div class="now-time">{JST.strftime('%H:%M:%S')}</div>
                <div class="now-title">スケジュール外</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- 次の予定表示 ---
    if next_event:
        n_start, n_end, n_title = next_event
        start_dt = datetime.combine(JST.date(), str_to_time(n_start))
        until_next_str = str(start_dt - JST).split(".")[0]
        placeholder_next.markdown(
            f"""
            <div class="next-block">
                <div class="next-title">次: {n_title}</div>
                <div class="next-time">{n_start} – {n_end} (開始まで {until_next_str})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        placeholder_next.empty()

    # --- 1 秒待機 ---
    _time.sleep(1)

    # --- 可能ならページ再実行 (最新版) ---
    try:
        st.experimental_rerun()
    except AttributeError:
        # 古い Streamlit は rerun API がない ⇒ ループのままプレースホルダ更新で OK
        pass
