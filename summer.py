"""
リアルタイム・スケジュールボード（現在パネルさらに10%縮小）
==============================================================
* 現在セッションパネル：`min-height` を **60 vh**（以前より約 10 % 短縮）
* 内側余白も `padding: 24px 20px` に絞り、フォントサイズはそのまま
* 他の部分（スローガン・次の予定など）は変更なし
"""

from __future__ import annotations

import time as _time
from datetime import datetime, time, timedelta
from typing import List, Tuple

import streamlit as st

st.set_page_config(page_title="3R3 スケジュールボード デモ", page_icon="🕒", layout="wide", initial_sidebar_state="collapsed")

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

st.markdown(
    """
    <style>
        body, .stApp { background:#ffffff; color:#000000; }
        .slogan { font-size: 36px; font-weight:700; text-align:center; margin:6px 0; }
        .current-time { font-size:28px; font-weight:600; text-align:center; margin-bottom:10px; }
        .now-panel { width:90%; min-height:60vh; border-radius:24px; padding:24px 20px; background:#fff3e0; border:4px solid #ff9800; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.15); margin:auto auto 24px auto; display:flex; flex-direction:column; justify-content:center; align-items:center; }
        .session-title { font-size:72px; font-weight:900; margin-bottom:18px; }
        .time-remaining { font-size:120px; font-weight:900; margin-bottom:28px; }
        .progress-outer { width:90%; height:40px; background:#eeeeee; border-radius:20px; overflow:hidden; }
        .progress-inner { height:100%; background:#ff9800; width:0%; }
        .next-panel { width:90%; padding:12px; background:#e3f2fd; border:3px solid #2196f3; border-radius:16px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.1); margin:auto; }
        .next-title { font-size:32px; font-weight:700; }
        .next-time { font-size:24px; margin-top:6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

def str_to_time(hm: str) -> time:
    return datetime.strptime(hm, "%H:%M").time()

def get_current_and_next(now_dt: datetime):
    now_ev, next_ev = None, None
    for s, e, label in SCHEDULE:
        st_t, ed_t = str_to_time(s), str_to_time(e)
        if st_t <= now_dt.time() <= ed_t:
            now_ev = (s, e, label)
        elif now_dt.time() < st_t and next_ev is None:
            next_ev = (s, e, label)
    return now_ev, next_ev

st.markdown("<div class='slogan'>つらかったと思える夏に！3R3ファミリー</div>", unsafe_allow_html=True)
ph_time, ph_now, ph_next = st.empty(), st.empty(), st.empty()

while True:
    JST = datetime.utcnow() + timedelta(hours=9)
    now_event, next_event = get_current_and_next(JST)

    ph_time.markdown(f"<div class='current-time'>{JST.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

    if now_event:
        s, e, title = now_event
        start_dt, end_dt = datetime.combine(JST.date(), str_to_time(s)), datetime.combine(JST.date(), str_to_time(e))
        total, elapsed = (end_dt - start_dt).total_seconds(), (JST - start_dt).total_seconds()
        remaining_str, pct = str(end_dt - JST).split(".")[0], int(elapsed/total*100)
        ph_now.markdown(f"""<div class='now-panel'><div class='session-title'>{title}</div><div class='time-remaining'>残り {remaining_str}</div><div class='progress-outer'><div class='progress-inner' style='width:{pct}%;'></div></div></div>""", unsafe_allow_html=True)
    else:
        ph_now.markdown("<div class='now-panel'><div class='session-title'>スケジュール外</div></div>", unsafe_allow_html=True)

    if next_event:
        ns, ne, nt = next_event
        until_next = str(datetime.combine(JST.date(), str_to_time(ns)) - JST).split(".")[0]
        ph_next.markdown(f"""<div class='next-panel'><div class='next-title'>次: {nt}</div><div class='next-time'>{ns} – {ne} (開始まで {until_next})</div></div>""", unsafe_allow_html=True)
    else:
        ph_next.empty()

    _time.sleep(1)
    try:
        st.experimental_rerun()
    except AttributeError:
        pass
