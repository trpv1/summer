"""
リアルタイム・スケジュールボード (1 秒更新)
========================================
* **10 : 25 スタート、1 分刻みの 11 セッション**
* 本日のタイムテーブル一覧は非表示
* 1 秒ごとに現在時刻・残り時間・次の予定を自動更新
* **Streamlit どのバージョンでも動く** ように、
  * `st.experimental_rerun()` が無い場合は `st.experimental_set_query_params()` で強制リロード

起動：
```bash
streamlit run big_schedule_board.py
```
"""

from __future__ import annotations

import random
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


def get_current_and_next(jst_now) -> tuple | tuple[None, None]:
    now_ev = None
    next_ev = None
    for start, end, label in SCHEDULE:
        start_t, end_t = str_to_time(start), str_to_time(end)
        if start_t <= jst_now.time() <= end_t:
            now_ev = (start, end, label)
        elif jst_now.time() < start_t and next_ev is None:
            next_ev = (start, end, label)
    return now_ev, next_ev

# -----------------------------------------------------------------------------
# メイン表示用プレースホルダ
# -----------------------------------------------------------------------------
placeholder_now  = st.empty()
placeholder_next = st.empty()

# -----------------------------------------------------------------------------
# ループ：1 秒ごとに更新
# -----------------------------------------------------------------------------
while True:
    JST = datetime.utcnow() + timedelta(hours=9)
    now_event, next_event = get_current_and_next(JST)

    # --- 現在セッション ---
    if now_event:
        start, end, title = now_event
        end_dt = datetime.combine(JST.date(), str_to_time(end))
        remaining = end_dt - JST
        remaining_str = str(remaining).split(".")[0]
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

    # --- 次の予定 ---
    if next_event:
        n_start, n_end, n_title = next_event
        start_dt = datetime.combine(JST.date(), str_to_time(n_start))
        until_next = start_dt - JST
        until_next_str = str(until_next).split(".")[0]

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

    # 1 秒待機
    _time.sleep(1)

    # ----------------------------------------------------------
    # 強制リロード（環境に合わせて二段構え）
    # ----------------------------------------------------------
    try:
        st.experimental_rerun()
    except AttributeError:
        # fallback: 乱数クエリパラメータで URL を書き換え → rerun
        try:
            st.experimental_set_query_params(_=random.random())
        except AttributeError:
            # それでも無理ならループ継続（画面上のプレースホルダは更新され続ける）
            pass
