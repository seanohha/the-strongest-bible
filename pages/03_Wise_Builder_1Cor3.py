import folium
import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen, MeasureControl, MiniMap
from streamlit_folium import st_folium

st.set_page_config(page_title="지혜로운 건축자 - 고전 3장", page_icon="🏗️", layout="wide")

BASEMAPS = {
    "아주 밝은 지도(추천)": {"tiles": "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png", "attr": "© OpenStreetMap contributors © CARTO", "name": "아주 밝은 지도"},
    "밝은 지도": {"tiles": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", "attr": "© OpenStreetMap contributors © CARTO", "name": "밝은 지도"},
    "기본 지도": {"tiles": "OpenStreetMap", "attr": None, "name": "기본 지도"},
}

TYPE_HEX = {
    "도시 배경": "#2563eb",
    "교회 문제": "#dc2626",
    "사역자": "#7c3aed",
    "성장": "#16a34a",
    "터": "#111827",
    "심판": "#f59e0b",
}

LOCATIONS = [
    {"id": 1, "name": "고린도", "modern": "Corinth, Greece", "lat": 37.9060, "lon": 22.8790, "type": "도시 배경", "refs": "고전 3:1–15", "summary": "헬라의 상업·항구 도시로 물질적 번성과 우상숭배, 도덕적 타락이 공존하던 곳입니다.", "theology": "세상의 가치관이 교회 안으로 들어올 때 교회는 분열과 미성숙에 빠집니다."},
    {"id": 2, "name": "교회 공동체", "modern": "Corinthian Church", "lat": 37.9068, "lon": 22.8820, "type": "교회 문제", "refs": "고전 3:1–4", "summary": "바울파, 아볼로파로 나뉘어 시기와 분쟁을 드러낸 공동체입니다.", "theology": "은사가 많아도 그리스도 중심이 아니면 영적으로 어린아이에 머물 수 있습니다."},
    {"id": 3, "name": "밭과 집", "modern": "God's field and building", "lat": 37.9085, "lon": 22.8750, "type": "성장", "refs": "고전 3:6–9", "summary": "바울은 심고 아볼로는 물을 주었지만 자라게 하시는 분은 하나님뿐입니다.", "theology": "사역자는 주인이 아니라 종이며, 교회는 하나님의 밭이요 하나님의 집입니다."},
    {"id": 4, "name": "터: 예수 그리스도", "modern": "Foundation", "lat": 37.9045, "lon": 22.8765, "type": "터", "refs": "고전 3:10–11", "summary": "교회의 유일한 터는 예수 그리스도입니다.", "theology": "교회는 사람의 재능, 부서, 훈련, 리더십 위가 아니라 그리스도 위에 세워져야 합니다."},
    {"id": 5, "name": "불의 시험", "modern": "Day of testing", "lat": 37.9028, "lon": 22.8835, "type": "심판", "refs": "고전 3:12–15", "summary": "각 사람이 무엇으로 교회를 세웠는지는 그 날에 불로 드러납니다.", "theology": "겉보기 성과가 아니라 그리스도와 말씀 위에 세운 공적만 남습니다."},
]

EVENTS = [
    {"step": 1, "loc_id": 1, "title": "고린도의 배경", "refs": "관점얻기", "text": "고린도는 번성한 상업·항구 도시였지만 우상숭배와 도덕적 타락이 만연했습니다. 교회는 세워졌지만 분열과 여러 문제를 겪었습니다.", "verse": "복음을 받은 지 오래되었지만 여전히 미성숙에 머물렀습니다.", "emotion": "혼합과 혼란", "christ": "복음은 세상의 가치관을 교회 안에 그대로 들여오는 것이 아니라 그리스도 중심으로 새롭게 하는 능력입니다.", "question": "내 신앙 안에 세상의 우월감과 비교 의식이 들어와 있지는 않습니까?"},
    {"step": 2, "loc_id": 2, "title": "어린아이 같은 신앙", "refs": "고전 3:1–2", "text": "바울은 고린도 교인들을 신령한 자가 아니라 육신에 속한 자, 곧 그리스도 안에서 어린아이처럼 대한다고 말합니다.", "verse": "내가 너희를 젖으로 먹이고 밥으로 아니하였노니.", "emotion": "미성숙", "christ": "그리스도의 마음을 품지 않는 신앙은 지식과 은사가 있어도 어린아이의 수준에 머뭅니다.", "question": "나는 말씀의 단단한 음식을 감당할 만큼 성숙해지고 있습니까?"},
    {"step": 3, "loc_id": 2, "title": "시기와 분쟁", "refs": "고전 3:3–4", "text": "고린도 교회 안에는 시기와 분쟁이 있었고, 사람을 따라 바울파와 아볼로파로 나뉘었습니다.", "verse": "너희 가운데 시기와 분쟁이 있으니.", "emotion": "비교와 분열", "christ": "사람을 자랑하면 몸이 찢어지지만, 그리스도를 붙들면 몸이 하나 됩니다.", "question": "나는 특정 사람, 부서, 훈련, 사역을 자랑하며 다른 사람을 판단한 적이 있습니까?"},
    {"step": 4, "loc_id": 3, "title": "심는 이와 물 주는 이", "refs": "고전 3:5–9", "text": "바울은 자신과 아볼로를 주께서 맡기신 대로 섬긴 사역자라고 설명합니다. 심고 물 주는 역할은 다르지만 자라게 하시는 이는 하나님뿐입니다.", "verse": "나는 심었고 아볼로는 물을 주었으되 오직 하나님께서 자라나게 하셨나니.", "emotion": "겸손한 섬김", "christ": "사역자는 주인이 아니라 그리스도의 일꾼이며 하나님의 비밀을 맡은 종입니다.", "question": "내가 맡은 섬김을 주인의 자리에서 하지 않고 종의 자리에서 하고 있습니까?"},
    {"step": 5, "loc_id": 4, "title": "유일한 터", "refs": "고전 3:10–11", "text": "바울은 지혜로운 건축자처럼 터를 닦았고, 그 터는 예수 그리스도라고 말합니다. 다른 터는 없습니다.", "verse": "이 터는 곧 예수 그리스도라.", "emotion": "본질 회복", "christ": "교회의 기초와 머리는 예수 그리스도입니다. 모든 사역은 그분 위에 세워져야 합니다.", "question": "내 공동체와 사역의 실제 중심은 예수님입니까, 아니면 사람의 성과와 전통입니까?"},
    {"step": 6, "loc_id": 5, "title": "불로 드러나는 공적", "refs": "고전 3:12–15", "text": "금·은·보석으로 세웠는지, 나무·풀·짚으로 세웠는지는 그 날에 불로 드러납니다.", "verse": "그 불이 각 사람의 공적이 어떠한 것을 시험할 것임이라.", "emotion": "두려운 점검", "christ": "영원히 남는 것은 사람의 영광이 아니라 살아 있는 하나님의 말씀과 그리스도 위에 세운 삶입니다.", "question": "이번 주 내가 그리스도 위에 남는 공적을 세우기 위해 구체적으로 할 수 있는 일은 무엇입니까?"},
]


def add_selected_basemap(m, basemap_name):
    cfg = BASEMAPS[basemap_name]
    kwargs = {"tiles": cfg["tiles"], "name": cfg["name"], "overlay": False, "control": False}
    if cfg["attr"]:
        kwargs["attr"] = cfg["attr"]
    folium.TileLayer(**kwargs).add_to(m)


def add_marker(m, loc, active=False):
    color = TYPE_HEX.get(loc["type"], "#333")
    size = 44 if active else 34
    html = f"""
    <div style="width:{size}px;height:{size}px;border-radius:50%;background:{color};color:white;border:4px solid white;box-shadow:0 3px 12px rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:{17 if active else 15}px;">{loc['id']}</div>
    """
    popup = f"""
    <div style='width:300px'>
      <h4>{loc['id']}. {loc['name']}</h4>
      <b>현재 위치/개념:</b> {loc['modern']}<br>
      <b>유형:</b> {loc['type']}<br>
      <b>본문:</b> {loc['refs']}<br><br>
      <b>내용:</b><br>{loc['summary']}<br><br>
      <b>신학적 의미:</b><br>{loc['theology']}
    </div>
    """
    folium.Marker(
        [loc["lat"], loc["lon"]],
        popup=folium.Popup(popup, max_width=340),
        tooltip=folium.Tooltip(f"{loc['id']}. {loc['name']} ({loc['type']})", sticky=True),
        icon=folium.DivIcon(html=html, class_name="clean-number-marker", icon_size=(size, size), icon_anchor=(size // 2, size // 2)),
    ).add_to(m)


def draw_map(step, basemap, show_context):
    current = EVENTS[step - 1]
    current_loc = next(loc for loc in LOCATIONS if loc["id"] == current["loc_id"])
    m = folium.Map(location=[37.906, 22.879], zoom_start=15, tiles=None, prefer_canvas=True)
    add_selected_basemap(m, basemap)
    Fullscreen().add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    MeasureControl(primary_length_unit="meters").add_to(m)
    visible_ids = {event["loc_id"] for event in EVENTS[:step]}
    for loc in LOCATIONS:
        if show_context or loc["id"] in visible_ids:
            add_marker(m, loc, active=(loc["id"] == current_loc["id"]))
    concept_route = [(loc["lat"], loc["lon"]) for loc in LOCATIONS]
    folium.PolyLine(concept_route[: max(2, min(step, len(concept_route)))], color="#5b21b6", weight=6, opacity=.9, dash_array="8, 10", tooltip="논리 흐름: 배경 → 문제 → 본질 → 점검").add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)
    m.fit_bounds([[37.900, 22.870], [37.912, 22.888]])
    return m, current

with st.sidebar:
    st.markdown("## 📖 최신 질문지")
    st.info("고린도전서 3:1–15 — 지혜로운 건축자")
    st.header("지도 설정")
    step = st.slider("시점 선택", 1, len(EVENTS), len(EVENTS))
    basemap = st.radio("배경 지도", list(BASEMAPS.keys()), index=0)
    show_context = st.checkbox("전체 흐름 배경으로 함께 보기", True)

st.title("🏗️ 지혜로운 건축자")
st.caption("고린도전서 3:1–15 | 미성숙 · 분열 · 사역자의 역할 · 그리스도라는 터 · 불의 시험")

left, right = st.columns([1.35, .65], gap="large")
with left:
    m, current = draw_map(step, basemap, show_context)
    st_folium(m, width=None, height=700, key=f"wise-builder-{step}-{basemap}-{show_context}")

with right:
    st.subheader(f"⏱️ 현재 시점 {current['step']}/{len(EVENTS)}")
    st.markdown(f"### {current['title']}")
    st.caption(current["refs"])
    st.write(current["text"])
    st.markdown("#### 📖 핵심 본문")
    st.info(current["verse"])
    st.markdown("#### 💔 상태/감정 레이어")
    st.warning(current["emotion"])
    st.markdown("#### ✝️ 복음 연결 / 신학")
    st.info(current["christ"])
    st.markdown("#### 💬 나눔 질문")
    st.success(current["question"])
    st.divider()
    st.subheader("📌 전체 흐름")
    for event in EVENTS:
        prefix = "👉 " if event["step"] == current["step"] else ""
        with st.expander(f"{prefix}{event['step']}. {event['title']} ({event['refs']})", expanded=event["step"] == current["step"]):
            st.write(event["text"])
            st.caption(event["question"])
    st.divider()
    st.subheader("개념/장소 표")
    st.dataframe(pd.DataFrame(LOCATIONS)[["id", "name", "modern", "type", "refs"]], hide_index=True, use_container_width=True)

st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 🌱 자라게 하시는 하나님")
    st.write("사역자는 심고 물을 줄 뿐, 교회를 자라게 하시는 분은 하나님뿐입니다.")
with c2:
    st.markdown("### 🪨 유일한 터")
    st.write("교회의 유일한 기초는 예수 그리스도입니다. 다른 터는 없습니다.")
with c3:
    st.markdown("### 🔥 불의 시험")
    st.write("그 날에는 무엇으로 교회를 세웠는지가 드러납니다. 말씀과 그리스도 위에 세운 것만 남습니다.")

st.warning("고린도 위치는 실제 지리이며, 지도 위 일부 마커는 본문 흐름을 설명하기 위한 개념적 배치입니다.")
