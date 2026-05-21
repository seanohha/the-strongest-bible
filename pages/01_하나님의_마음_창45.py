import folium
import pandas as pd
import streamlit as st
from folium.plugins import AntPath, Fullscreen, MeasureControl, MiniMap
from streamlit_folium import st_folium

st.set_page_config(page_title="하나님의 마음 - 창세기 45장", page_icon="🕊️", layout="wide")

BASEMAPS = {
    "아주 밝은 지도(추천)": {
        "tiles": "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
        "attr": "© OpenStreetMap contributors © CARTO",
        "name": "아주 밝은 지도",
    },
    "밝은 지도": {
        "tiles": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        "attr": "© OpenStreetMap contributors © CARTO",
        "name": "밝은 지도",
    },
    "기본 지도": {"tiles": "OpenStreetMap", "attr": None, "name": "기본 지도"},
    "지형 지도": {"tiles": "OpenTopoMap", "attr": None, "name": "지형 지도"},
}

TYPE_HEX = {
    "출발": "#2563eb",
    "시험": "#f59e0b",
    "계시": "#7c3aed",
    "용서": "#dc2626",
    "초청": "#16a34a",
    "보존": "#0891b2",
}

LOCATIONS = [
    {
        "id": 1,
        "name": "가나안 / 야곱의 거처",
        "modern": "Hebron / southern Canaan, West Bank",
        "lat": 31.5326,
        "lon": 35.0998,
        "type": "출발",
        "refs": "창 42–44장 배경",
        "summary": "기근으로 인해 야곱이 아들들을 애굽으로 보내 양식을 구하게 한 출발 배경입니다.",
        "theology": "하나님은 기근이라는 위기를 통해 감추어진 가족의 죄와 상처를 드러내고 회복의 길을 여십니다.",
    },
    {
        "id": 2,
        "name": "애굽 / 요셉의 통치 자리",
        "modern": "Egypt / Nile Delta direction",
        "lat": 30.0444,
        "lon": 31.2357,
        "type": "계시",
        "refs": "창 45:1–15",
        "summary": "요셉이 형들에게 자신의 정체를 밝히고, 하나님의 섭리를 고백하며, 가족을 고센으로 초청하는 중심 장소입니다.",
        "theology": "형들이 팔아버린 장소가 아니라 하나님이 먼저 보내신 자리로 해석되는 구원의 무대입니다.",
    },
    {
        "id": 3,
        "name": "고센 땅",
        "modern": "Eastern Nile Delta / Wadi Tumilat area, Egypt",
        "lat": 30.5830,
        "lon": 31.5000,
        "type": "초청",
        "refs": "창 45:10–11",
        "summary": "요셉이 아버지 야곱과 가족, 가축과 모든 소유를 머물게 하려 한 땅입니다.",
        "theology": "하나님은 한 개인의 성공이 아니라 언약 공동체 전체의 생명을 보존하십니다.",
    },
]

EVENTS = [
    {
        "step": 1,
        "loc_id": 1,
        "title": "기근과 애굽행",
        "refs": "창 42–44장 배경",
        "text": "가나안의 기근 때문에 야곱의 아들들은 애굽으로 양식을 구하러 내려옵니다. 그들은 총리가 된 요셉을 알아보지 못하고, 요셉의 꿈처럼 그 앞에 엎드립니다.",
        "verse": "기근 속에서 형들은 애굽으로 내려가고, 요셉 앞에 엎드리게 됩니다.",
        "emotion": "두려움과 필요",
        "theology": "하나님은 결핍을 통해 감추어진 죄와 관계의 문제를 다루기 시작하십니다.",
        "christ": "인간의 필요는 결국 참 생명의 공급자이신 그리스도께로 이끕니다.",
        "question": "내 삶의 결핍과 위기가 하나님께 나아가는 통로가 된 적이 있습니까?",
    },
    {
        "step": 2,
        "loc_id": 2,
        "title": "요셉의 시험과 형들의 변화 확인",
        "refs": "창 44:19–34",
        "text": "요셉은 베냐민 문제를 통해 형들이 과거처럼 또 다른 라헬의 아들을 버릴 것인지 확인합니다. 유다는 자신이 대신 종이 되겠다고 청원합니다.",
        "verse": "주의 종으로 그 아이를 대신하여 머물러 있어 내 주의 종이 되게 하시고.",
        "emotion": "회개와 책임",
        "theology": "진정한 변화는 말이 아니라 대신 책임지려는 태도로 드러납니다.",
        "christ": "유다의 대속적 태도는 장차 유다 지파에서 오실 예수 그리스도의 대속을 희미하게 보여줍니다.",
        "question": "나는 과거의 잘못을 회피합니까, 아니면 누군가를 살리기 위해 책임을 지려 합니까?",
    },
    {
        "step": 3,
        "loc_id": 2,
        "title": "요셉의 눈물",
        "refs": "창 45:1–2",
        "text": "유다의 간절한 청원 앞에서 요셉은 더 이상 정을 억제하지 못하고 모든 사람을 물러가게 한 뒤 큰 소리로 웁니다.",
        "verse": "요셉이 큰 소리로 우니 애굽 사람에게 들리며 바로의 궁중에 들리더라.",
        "emotion": "억눌린 상처와 사랑의 폭발",
        "theology": "하나님의 마음은 차가운 판결이 아니라 생명을 살리려는 뜨거운 긍휼로 나타납니다.",
        "christ": "예수님도 죄인을 향해 긍휼히 여기시며 눈물 흘리시는 주님이십니다.",
        "question": "나는 상처받은 자리에서도 하나님의 긍휼을 품을 수 있습니까?",
    },
    {
        "step": 4,
        "loc_id": 2,
        "title": "나는 요셉이라",
        "refs": "창 45:3–4",
        "text": "요셉은 형들에게 자신의 정체를 밝힙니다. 형들은 놀라서 대답하지 못하고, 요셉은 가까이 오라고 부릅니다.",
        "verse": "나는 당신들의 아우 요셉이니 당신들이 애굽에 판 자라.",
        "emotion": "충격과 두려움",
        "theology": "죄가 드러나는 순간은 두렵지만, 하나님은 그 순간을 회복의 시작으로 사용하십니다.",
        "christ": "십자가에 못 박은 예수를 하나님이 주와 그리스도가 되게 하셨다는 복음 앞에서 사람들은 ‘우리가 어찌할꼬’라고 반응합니다.",
        "question": "내 죄가 드러날 때 나는 숨습니까, 아니면 은혜 앞에 가까이 나아갑니까?",
    },
    {
        "step": 5,
        "loc_id": 2,
        "title": "근심하지 마소서",
        "refs": "창 45:5",
        "text": "요셉은 형들에게 자신을 판 일로 근심하거나 한탄하지 말라고 말합니다. 이유는 하나님이 생명을 구원하시려고 자신을 먼저 보내셨기 때문입니다.",
        "verse": "하나님이 생명을 구원하시려고 나를 당신들보다 먼저 보내셨나이다.",
        "emotion": "용서와 위로",
        "theology": "용서는 죄를 부정하는 것이 아니라, 인간의 죄보다 크신 하나님의 섭리를 보는 데서 시작됩니다.",
        "christ": "십자가는 인간의 죄가 가장 크게 드러난 자리이지만 동시에 하나님의 구원이 가장 분명히 드러난 자리입니다.",
        "question": "내가 붙들고 있는 상처보다 하나님의 더 큰 뜻을 보기 시작해야 할 영역은 어디입니까?",
    },
    {
        "step": 6,
        "loc_id": 2,
        "title": "당신들이 아니요 하나님이시라",
        "refs": "창 45:6–8",
        "text": "요셉은 앞으로 5년의 흉년이 남았고, 하나님이 큰 구원으로 생명을 보존하시기 위해 자신을 애굽으로 보내셨다고 고백합니다.",
        "verse": "나를 이리로 보낸 이는 당신들이 아니요 하나님이시라.",
        "emotion": "섭리의 확신",
        "theology": "하나님의 주권은 인간의 악을 무효화하는 것이 아니라, 그 악을 넘어 생명을 살리는 구원으로 이끄십니다.",
        "christ": "사도행전은 예수님의 고난도 하나님이 미리 알리신 일을 이루신 것이라고 선포합니다.",
        "question": "내 인생의 고난을 ‘왜 나에게?’에서 ‘하나님이 무엇을 이루시는가?’로 바라볼 수 있습니까?",
    },
    {
        "step": 7,
        "loc_id": 3,
        "title": "고센으로 초청",
        "refs": "창 45:9–13",
        "text": "요셉은 형들에게 속히 아버지께 올라가 자신이 살아 있고 애굽의 주가 되었음을 전하며, 가족 전체를 고센으로 데려오라고 합니다.",
        "verse": "고센 땅에 머물며 나와 가깝게 하소서.",
        "emotion": "초청과 보호",
        "theology": "하나님이 주신 지위와 축복은 자기 보상이 아니라 생명을 살기 위한 사명입니다.",
        "christ": "그리스도는 자기에게 가까이 오라고 부르시며, 생명을 얻은 자들을 보호하십니다.",
        "question": "내가 가진 자리와 자원은 나를 위한 보상입니까, 아니면 누군가를 살리기 위한 사명입니까?",
    },
    {
        "step": 8,
        "loc_id": 2,
        "title": "입맞춤과 대화의 회복",
        "refs": "창 45:14–15",
        "text": "요셉은 베냐민과 형들을 안고 울며 입맞춥니다. 그제서야 형들은 요셉과 말하기 시작합니다.",
        "verse": "요셉이 또 형들과 입맞추며 안고 우니 형들이 그제서야 요셉과 말하니라.",
        "emotion": "화해와 관계 회복",
        "theology": "하나님의 마음은 죄인을 멀리 밀어내는 것이 아니라, 회개한 자를 가까이 불러 관계를 회복시키는 것입니다.",
        "christ": "복음은 하나님과 원수 된 자들을 그리스도 안에서 화목하게 합니다.",
        "question": "이번 주 내가 먼저 화해의 손길을 내밀 수 있는 사람은 누구입니까?",
    },
]

ROUTES = {
    "가나안 → 애굽": [(31.5326, 35.0998), (31.2, 34.8), (30.6, 33.0), (30.0444, 31.2357)],
    "애굽 → 고센 초청": [(30.0444, 31.2357), (30.5830, 31.5000)],
}


def add_selected_basemap(m, basemap_name):
    cfg = BASEMAPS[basemap_name]
    kwargs = {"tiles": cfg["tiles"], "name": cfg["name"], "overlay": False, "control": False}
    if cfg["attr"]:
        kwargs["attr"] = cfg["attr"]
    folium.TileLayer(**kwargs).add_to(m)


def add_optional_basemaps(m, selected):
    for name, cfg in BASEMAPS.items():
        if name == selected:
            continue
        kwargs = {"tiles": cfg["tiles"], "name": cfg["name"], "overlay": False, "control": True, "show": False}
        if cfg["attr"]:
            kwargs["attr"] = cfg["attr"]
        folium.TileLayer(**kwargs).add_to(m)


def make_popup(loc):
    return f"""
    <div style='width:300px'>
      <h4>{loc['id']}. {loc['name']}</h4>
      <b>현재 위치:</b> {loc['modern']}<br>
      <b>유형:</b> {loc['type']}<br>
      <b>본문:</b> {loc['refs']}<br><br>
      <b>사건:</b><br>{loc['summary']}<br><br>
      <b>신학적 의미:</b><br>{loc['theology']}
    </div>
    """


def add_marker(m, loc, active=False):
    color = TYPE_HEX.get(loc["type"], "#333")
    size = 44 if active else 34
    html = f"""
    <div style="width:{size}px;height:{size}px;border-radius:50%;background:{color};color:white;border:4px solid white;box-shadow:0 3px 12px rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:{17 if active else 15}px;">{loc['id']}</div>
    """
    folium.Marker(
        [loc["lat"], loc["lon"]],
        popup=folium.Popup(make_popup(loc), max_width=340),
        tooltip=folium.Tooltip(f"{loc['id']}. {loc['name']} ({loc['modern']})", sticky=True),
        icon=folium.DivIcon(html=html, class_name="clean-number-marker", icon_size=(size, size), icon_anchor=(size // 2, size // 2)),
    ).add_to(m)


def draw_map(basemap, route_width, show_context, show_goshen, step, current_loc):
    m = folium.Map(location=[30.7, 33.1], zoom_start=6, tiles=None, prefer_canvas=True)
    add_selected_basemap(m, basemap)
    add_optional_basemaps(m, basemap)
    Fullscreen().add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    MeasureControl(primary_length_unit="kilometers").add_to(m)

    if show_context:
        folium.PolyLine(ROUTES["가나안 → 애굽"], color="#9ca3af", weight=3, opacity=.35, dash_array="4, 8", tooltip="가나안에서 애굽으로 내려가는 배경 경로").add_to(m)

    if step >= 1:
        AntPath(ROUTES["가나안 → 애굽"], color="#5b21b6", weight=route_width, opacity=.95, delay=900, dash_array=[15, 25], tooltip="기근 속 애굽행").add_to(m)

    if show_goshen and step >= 7:
        folium.PolyLine(ROUTES["애굽 → 고센 초청"], color="#ffffff", weight=route_width + 4, opacity=.9, dash_array="10, 10").add_to(m)
        folium.PolyLine(ROUTES["애굽 → 고센 초청"], color="#16a34a", weight=route_width, opacity=.95, dash_array="10, 10", tooltip="고센으로의 초청과 생명 보존").add_to(m)

    visible_ids = {e["loc_id"] for e in EVENTS[:step]}
    if show_goshen and step >= 7:
        visible_ids.add(3)

    for loc in LOCATIONS:
        if loc["id"] in visible_ids or show_context:
            add_marker(m, loc, active=(loc["id"] == current_loc["id"]))

    folium.LayerControl(collapsed=True).add_to(m)
    m.fit_bounds([[29.7, 30.7], [32.0, 35.4]])
    return m

with st.sidebar:
    st.markdown("## 📖 최신 질문지")
    st.info("창세기 45:1–15 — 하나님의 마음")
    st.header("지도 설정")
    step = st.slider("시점 선택", 1, len(EVENTS), len(EVENTS))
    basemap = st.radio("배경 지도", list(BASEMAPS.keys()), index=0)
    show_context = st.checkbox("전체 배경 함께 보기", True)
    show_goshen = st.checkbox("고센 초청/보존 레이어 표시", True)
    route_width = st.slider("경로 선 굵기", 4, 12, 8)

current = EVENTS[step - 1]
current_loc = next(loc for loc in LOCATIONS if loc["id"] == current["loc_id"])

st.title("🕊️ 하나님의 마음 — 요셉의 용서와 화해")
st.caption("창세기 45:1–15 | 기근 · 시험 · 눈물 · 용서 · 생명 보존 · 그리스도 예표")

left, right = st.columns([1.35, .65], gap="large")

with left:
    m = draw_map(basemap, route_width, show_context, show_goshen, step, current_loc)
    st_folium(m, width=None, height=700, key=f"gen45-{step}-{basemap}-{show_context}-{show_goshen}-{route_width}")

with right:
    st.subheader(f"⏱️ 현재 시점 {current['step']}/{len(EVENTS)}")
    st.markdown(f"### {current['title']}")
    st.caption(current["refs"])
    st.write(current["text"])

    st.markdown("#### 📖 핵심 본문")
    st.info(current["verse"])

    st.markdown("#### 💔 감정 레이어")
    st.warning(current["emotion"])

    st.markdown("#### 🧭 신학 핵심")
    st.info(current["theology"])

    st.markdown("#### ✝️ 그리스도 예표 / 복음 연결")
    st.info(current["christ"])

    st.markdown("#### 💬 나눔 질문")
    st.success(current["question"])

    st.divider()
    st.subheader("📌 전체 사건 순서")
    for event in EVENTS:
        prefix = "👉 " if event["step"] == current["step"] else ""
        with st.expander(f"{prefix}{event['step']}. {event['title']} ({event['refs']})", expanded=event["step"] == current["step"]):
            st.write(event["text"])
            st.caption(event["question"])

    st.divider()
    st.subheader("장소별 표")
    st.dataframe(pd.DataFrame(LOCATIONS)[["id", "name", "modern", "type", "refs"]], hide_index=True, use_container_width=True)

st.divider()

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 🧎 유다의 변화")
    st.write("요셉을 팔던 유다가 이제는 베냐민을 위해 자신을 대신 내어놓으려 합니다.")
with c2:
    st.markdown("### 🕊️ 요셉의 용서")
    st.write("요셉은 형들의 죄를 부정하지 않지만, 그 죄보다 크신 하나님의 섭리를 바라봅니다.")
with c3:
    st.markdown("### ✝️ 복음 연결")
    st.write("요셉의 생명 보존은 장차 예수 그리스도를 통한 영원한 구원을 예표합니다.")

st.warning("고대 지명과 이동 경로는 성경공부용 근사 시각화입니다. 정확한 고고학·역사지리 논증을 대체하지 않습니다.")
