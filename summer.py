"""
リアルタイム・スケジュールボード（余白5%縮小＋スローガン）
===============================================================
* 現在セッションパネルの **縦幅を 5 % 短縮**：`min-height: 66vh` + padding 32 px
* 画面最上部中央にスローガン追加
```
つらかったと思える夏に！3R3ファミリー
```
* 他のレイアウト・機能はそのまま
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
# タイムテーブル（JST） 10:40 から 1 分刻み
# -----------------------------------------------------------------------------
SCHEDULE: List[Tuple[str, str, str]] = [
    ("10:40", "10:41", "授業前"),
    ("10:41", "10:42", "テスト開始5分前カウントダウン"),
    ("10:42", "10:43", "テスト開始"),
    ("10:43", "10:44", "テスト終了5分前カウントダウン"),
    ("10:44", "10:45", "テスト終了採点"),
    ("10:45", "10:46", "とことん演習開始"),
    ("10:46", "10:47", "とことん演習終了5分前カウントダウン"),
    ("10:47", "10:48", "休憩時間"),
    ("10:48", "10:49", "休憩終了5分前カウントダウン"),
    ("10:49", "10:50", "授業開始"),
    ("10:50", "10:51", "授業終了10分前カウントダウン"),
]

# -----------------------------------------------------------------------------
# CSS スタイル
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        body, .stApp { background:#ffffff; color:#000000; }

        /* スローガン */
        .slogan {
            font-size: 36px;
            font-weight: 700;
            text-align:center;
            margin-top:6px; margin-bottom:6px;
        }

        /* 現在時刻 */
        .current-time {
            font-size: 28px;
            font-weight: 600;
            text-align:center;
            margin-bottom:10px;
        }

        /* メインパネル (縦幅 66vh) */
        .now-panel {
            width: 90%;
            min-height: 66vh;  /* ← 5% 縮小 */
            border-radius: 24px;
            padding: 32px 20px; /* padding も少し減らす */
            background:#fff3e0;
            border: 4px solid #ff9800;
            text-align:center;
            box-shadow:0 4px 12px rgba(0,0,0,0.15);
            margin:auto auto 24px auto;
            display:flex; flex-direction:column; justify-content:center; align-items:center;
        }
        .session-title { font-size: 72px; font-weight: 900; margin-bottom:20px; }
        .time-remaining { font-size: 120px; font-weight: 900; margin-bottom:32px; }

        /* プログレスバー */
        .progress-outer {
            width: 90%;
            height: 40px;
            background:#eeeeee;
            border-radius: 20px;
            overflow:hidden;
        }
        .progress-inner { height: 100%; background:#ff9800; width:0%; }

        /* 次の予定 (横幅そろえ / 縦薄) */
        .next-panel {
            width: 90%;
            padding: 12px;
            background:#e3f2fd;
            border: 3px solid #2196f3;
            border-radius: 16px;
            text-align:center;
            box-shadow:0 2px 8px rgba(0,0,0,0.1);
            margin:auto;
        }
        .next-title { font-size: 32px; font-weight:700; }
        .next-time  { font-size: 24px; margin-top:6px; }
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
# 静的ヘッダ
# -----------------------------------------------------------------------------
st.markdown("<div class='slogan'>つらかったと思える夏に！3R3ファミリー</div>", unsafe_allow_html=True)

# プレースホルダ
ph_time   = st.empty()
ph_now    = st.empty()
ph_next   = st.empty()

# -----------------------------------------------------------------------------
# 更新ループ
# -----------------------------------------------------------------------------
while True:
    JST = datetime.utcnow() + timedelta(hours=9)
    now_event, next_event = get_current_and_next(JST)

    # 現在時刻
    ph_time.markdown(
        f"<div class='current-time'>{JST.strftime('%H:%M:%S')}</div>",
        unsafe_allow_html=True,
    )

    # 現在セッション
    if now_event:
        start_s, end_s, title = now_event
        start_dt = datetime.combine(JST.date(), str_to_time(start_s))
        end_dt   = datetime.combine(JST.date(), str_to_time(end_s))
        total_sec = (end_dt - start_dt).total_seconds()
        elapsed_sec = (JST - start_dt).total_seconds()
        remaining_str = str(end_dt - JST).split(".")[0]
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

    # 次の予定
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

    # 可能ならページ再実行
    try:
        st.experimental_rerun()
    except AttributeError:
        pass
