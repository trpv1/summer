"""
リアルタイム・スケジュールボード（タイムリミット強調版）
========================================================
* 10 : 25 スタート／1 分刻み（デモ用）
* **残り時間を極太・超特大フォントで中央表示**
* セッション進行度を 100% スケールの **プログレスバー** で可視化
* 現在時刻は上部中央に小さめに 1 行で表示
* 本日のタイムテーブル一覧は非表示
* 1 秒ごとに更新、非推奨 API 不使用で警告ゼロ
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
# CSS スタイル
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        body, .stApp { background:#ffffff; color:#000000; }

        /* 現在時刻 */
        .current-time {
            font-size: 32px;
            font-weight: 600;
            text-align:center;
            margin-bottom:14px;
        }

        /* メインパネル */
        .now-panel {
            border-radius: 24px;
            padding: 30px 20px;
            background:#fff3e0;
            border: 4px solid #ff9800;
            text-align:center;
            margin-bottom:40px;
            box-shadow:0 4px 12px rgba(0,0,0,0.15);
        }
        .session-title { font-size: 48px; font-weight: 800; margin-bottom:20px; }
        .time-remaining { font-size: 88px; font-weight: 900; margin-bottom:30px; }

        /* プログレスバー */
        .progress-outer {
            width: 80%;
            height: 30px;
            background:#eeeeee;
            border-radius: 15px;
            margin: 0 auto 10px auto;
            overflow:hidden;
        }
        .progress-inner {
            height: 100%;
            background:#ff9800;
            width:0%; /* JS で挿入 */
        }

        /* 次の予定 */
        .next-panel {
            border-radius: 16px;
            padding: 20px;
            background:#e3f2fd;
            border: 3px solid #2196f3;
            text-align:center;
            box-shadow:0 2px 8px rgba(0,0,0,0.1);
        }
        .next-title { font-size: 32px; font-weight:700; }
        .next-time  { font-size: 24px; margin-top:8px; }
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
    for start_s, end_s, label in SCHEDULE:
        s_t, e_t = str_to_time(start_s), str_to_time(end_s)
        if s_t <= now_dt.time() <= e_t:
            now_ev = (start_s, end_s, label)
        elif now_dt.time() < s_t and next_ev is None:
            next_ev = (start_s, end_s, label)
    return now_ev, next_ev

# -----------------------------------------------------------------------------
# プレースホルダ
# -----------------------------------------------------------------------------
ph_time   = st.empty()  # 現在時刻
ph_now    = st.empty()  # 現在セッション
ph_next   = st.empty()  # 次セッション

# -----------------------------------------------------------------------------
# ループ
# -----------------------------------------------------------------------------
while True:
    JST = datetime.utcnow() + timedelta(hours=9)
    now_event, next_event = get_current_and_next(JST)

    # ----- 現在時刻 (控えめ) -----
    ph_time.markdown(
        f"<div class='current-time'>{JST.strftime('%H:%M:%S')}</div>",
        unsafe_allow_html=True,
    )

    # ----- 現在セッション -----
    if now_event:
        start_s, end_s, title = now_event
        start_dt = datetime.combine(JST.date(), str_to_time(start_s))
        end_dt   = datetime.combine(JST.date(), str_to_time(end_s))
        total_sec = (end_dt - start_dt).total_seconds()
        elapsed_sec = (JST - start_dt).total_seconds()
        remaining_td = end_dt - JST
        remaining_str = str(remaining_td).split(".")[0]
        progress_pct = max(0, min(100, int(elapsed_sec / total_sec * 100)))

        ph_now.markdown(
            f"""
            <div class='now-panel'>
                <div class='session-title'>{title}</div>
                <div class='time-remaining'>残り {remaining_str}</div>
                <div class='progress-outer'>
                    <div class='progress-inner' style='width:{progress_pct}%;'></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        ph_now.markdown(
            "<div class='now-panel'><div class='session-title'>スケジュール外</div></div>",
            unsafe_allow_html=True,
        )

    # ----- 次の予定 -----
    if next_event:
        n_start, n_end, n_title = next_event
        start_dt = datetime.combine(JST.date(), str_to_time(n_start))
        until_next_str = str(start_dt - JST).split(".")[0]
        ph_next.markdown(
            f"""
            <div class='next-panel'>
                <div class='next-title'>次: {n_title}</div>
                <div class='next-time'>{n_start} – {n_end} (開始まで {until_next_str})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        ph_next.empty()

    # 1 秒待機
    _time.sleep(1)

    # 可能ならページ再実行（最新版のみ）
    try:
        st.experimental_rerun()
    except AttributeError:
        pass
