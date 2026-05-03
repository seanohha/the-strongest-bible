import math

import folium
import pandas as pd
import streamlit as st
from folium.plugins import AntPath, Fullscreen, MeasureControl, MiniMap
from streamlit_folium import st_folium

st.set_page_config(
    page_title="야곱의 여정 인터랙티브 성경지도",
    page_icon="🗺️",
    layout="wide",
)

# ------------------------------------------------------------
# 좌표 데이터
# ------------------------------------------------------------
# 주의: 고대 지명은 학자별 비정 차이가 있습니다.
# 아래 좌표는 성경공부용 근사값입니다.
# ------------------------------------------------------------
LOCATIONS = [
    {"id": 1, "name": "밧단아람 / 하란", "modern": "Harran, Türkiye", "lat": 36.8670, "lon": 39.0310, "type": "출발지", "refs": "창 31:1–3, 33:18", "summary": "야곱이 라반의 집에서 약 20년을 머문 뒤, 하나님의 명령을 따라 고향으로 향해 출발한 북메소포타미아 지역입니다.", "theology": "도망자의 긴 세월도 하나님의 약속 안에서는 귀환의 여정이 됩니다."},
    {"id": 2, "name": "얍복강", "modern": "Zarqa River, Jordan", "lat": 32.1830, "lon": 35.6160, "type": "전환점", "refs": "창 32:3–32, 호 12:3–4", "summary": "야곱이 에서를 두려워하며 사자를 보내고, 가족과 재산을 나누고, 밤에는 홀로 남아 하나님과 씨름한 곳입니다.", "theology": "진짜 문제는 에서가 아니라 하나님 앞에서 깨어지지 않은 야곱 자신이었습니다."},
    {"id": 3, "name": "에서와의 만남 장소", "modern": "얍복강 서쪽/요단 동편 추정, Jordan Valley", "lat": 32.1250, "lon": 35.5600, "type": "화해", "refs": "창 33:1–11", "summary": "야곱이 일곱 번 땅에 엎드리며 나아갔고, 에서가 달려와 안고 입맞추며 서로 운 장소로 추정됩니다.", "theology": "하나님과의 화해가 사람과의 화해로 이어졌습니다. 야곱은 에서의 얼굴에서 하나님의 얼굴을 본 것 같다고 고백합니다."},
    {"id": 4, "name": "세일", "modern": "Edom / southern Jordan, Petra–Showbak region", "lat": 30.3285, "lon": 35.4444, "type": "에서의 방향", "refs": "창 33:12–16", "summary": "에서가 돌아간 남쪽 에돔 산지 방향입니다. 실제 축척으로 보면 얍복강/세겜보다 훨씬 남쪽에 있습니다.", "theology": "화해는 이루어졌지만, 야곱의 부르심은 에서의 거처가 아니라 하나님이 명하신 벧엘을 향해 계속되어야 했습니다."},
    {"id": 5, "name": "숙곳", "modern": "Tell Deir Alla vicinity, Jordan", "lat": 32.1900, "lon": 35.6200, "type": "멈춤", "refs": "창 33:17", "summary": "야곱이 집을 짓고 가축을 위해 우릿간을 세운 곳입니다. 이름은 ‘장막/초막’을 뜻합니다.", "theology": "위기가 지나가자 야곱은 다시 머물기 시작합니다. 은혜 이후에도 순종은 계속되어야 합니다."},
    {"id": 6, "name": "세겜", "modern": "Nablus, Palestine / West Bank", "lat": 32.2211, "lon": 35.2544, "type": "부분 순종", "refs": "창 33:18–20", "summary": "야곱이 밧단아람에서부터 평안히 가나안 땅 세겜에 이르러 장막을 치고 밭을 사며 제단을 쌓은 곳입니다.", "theology": "제단을 쌓고 ‘엘엘로헤이스라엘’이라 고백했지만, 아직 벧엘까지는 가지 않았습니다."},
    {"id": 7, "name": "벧엘", "modern": "Beitin, Palestine / West Bank", "lat": 31.9410, "lon": 35.2330, "type": "가야 할 목적지", "refs": "창 28:10–22, 31:13, 35:1", "summary": "야곱이 처음 하나님을 만난 장소이며, 하나님께서 돌아가라고 명하신 목적지입니다. 창 33장에서는 아직 도달하지 못했습니다.", "theology": "벧엘은 완전한 순종의 자리입니다. 하나님을 만난 사람은 결국 하나님이 부르신 자리로 돌아가야 합니다."},
]

EVENTS = [
    {"step": 1, "title": "밧단아람/하란 출발", "refs": "창 31:1–3", "text": "하나님의 명령을 듣고 라반의 집을 떠나 고향으로 향함."},
    {"step": 2, "title": "얍복강 도착 전 두려움", "refs": "창 32:3–9", "text": "에서가 400명을 데리고 온다는 소식에 두려워하고, 무리를 두 떼로 나누고 기도함."},
    {"step": 3, "title": "예물 준비와 보냄", "refs": "창 32:13–21", "text": "에서의 감정을 풀기 위해 예물을 여러 떼로 나누어 먼저 보냄."},
    {"step": 4, "title": "얍복강 사건", "refs": "창 32:22–32", "text": "홀로 남은 야곱이 하나님과 씨름하고, 이름이 이스라엘로 바뀜."},
    {"step": 5, "title": "에서와의 만남", "refs": "창 33:1–11", "text": "야곱이 일곱 번 절하며 나아가고, 에서는 달려와 안고 입맞추며 화해함."},
    {"step": 6, "title": "에서는 세일로 돌아감", "refs": "창 33:12–16", "text": "에서는 함께 가자고 하지만 야곱은 사양하고, 에서는 남쪽 세일로 돌아감."},
    {"step": 7, "title": "야곱은 숙곳에 머묾", "refs": "창 33:17", "text": "야곱은 숙곳에 이르러 집과 우릿간을 지으며 머무름."},
    {"step": 8, "title": "세겜 도착과 제단", "refs": "창 33:18–20", "text": "밧단아람에서부터 평안히 세겜에 이르러 밭을 사고 제단을 쌓음."},
    {"step": 9, "title": "벧엘 — 아직 미도달", "refs": "창 28:10–22, 31:13", "text": "하나님이 명령하신 목적지는 벧엘이지만 창 33장에서는 아직 이르지 못함."},
]

ROUTE_JACOB_FULL = [(36.8670, 39.0310), (36.8000, 38.0000), (35.9000, 37.7000), (34.8000, 36.5000), (33.5000, 36.3000), (32.1830, 35.6160), (32.1250, 35.5600), (32.1900, 35.6200), (32.2211, 35.2544), (31.9410, 35.2330)]
ROUTE_JACOB_CANAAN = [(32.1830, 35.6160), (32.1250, 35.5600), (32.1900, 35.6200), (32.2211, 35.2544), (31.9410, 35.2330)]
ROUTE_ESAU = [(32.1250, 35.5600), (31.3000, 35.4800), (30.3285, 35.4444)]

TYPE_COLORS = {"출발지": "blue", "전환점": "purple", "화해": "red", "에서의 방향": "orange", "멈춤": "cadetblue", "부분 순종": "green", "가야 할 목적지": "darkred"}
TYPE_HEX = {"출발지": "#2563eb", "전환점": "#7c3aed", "화해": "#dc2626", "에서의 방향": "#ea580c", "멈춤": "#0891b2", "부분 순종": "#16a34a", "가야 할 목적지": "#991b1b"}


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def route_distance(points):
    return sum(haversine_km(a[0], a[1], b[0], b[1]) for a, b in zip(points[:-1], points[1:]))


def add_label(map_obj, loc):
    html = f"""
    <div style="
        background: rgba(255,255,255,0.96);
        border: 2px solid {TYPE_HEX.get(loc['type'], '#333')};
        border-radius: 8px;
        padding: 4px 7px;
        font-size: 13px;
        line-height: 1.15;
        white-space: nowrap;
        box-shadow: 0 2px 7px rgba(0,0,0,0.28);
    ">
        <b style="color:#111">{loc['name']}</b><br>
        <span style="font-size:10.5px;color:#444">({loc['modern']})</span>
    </div>
    """
    folium.Marker([loc["lat"], loc["lon"]], icon=folium.DivIcon(html=html)).add_to(map_obj)


def add_number_marker(map_obj, loc):
    color = TYPE_HEX.get(loc["type"], "#333")
    html = f"""
    <div style="
        width: 34px; height: 34px;
        border-radius: 50%;
        background: {color};
        color: white;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.45);
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 15px;
    ">{loc['id']}</div>
    """
    folium.Marker(
        [loc["lat"], loc["lon"]],
        popup=folium.Popup(make_popup(loc), max_width=340),
        tooltip=f"{loc['id']}. {loc['name']} ({loc['modern']})",
        icon=folium.DivIcon(html=html, icon_size=(34, 34), icon_anchor=(17, 17)),
    ).add_to(map_obj)


def make_popup(loc):
    return f"""
    <div style='width: 300px'>
        <h4>{loc['id']}. {loc['name']}</h4>
        <b>현재 위치:</b> {loc['modern']}<br>
        <b>유형:</b> {loc['type']}<br>
        <b>본문:</b> {loc['refs']}<br><br>
        <b>사건:</b><br>{loc['summary']}<br><br>
        <b>신학적 의미:</b><br>{loc['theology']}
    </div>
    """


st.title("🗺️ 야곱의 여정 인터랙티브 성경지도")
st.caption("창세기 28:10–33:20 | 실제 축척 모드 + 가나안 확대 모드 + 현대 지명 병기")

with st.sidebar:
    st.header("지도 설정")
    map_mode = st.radio("지도 모드", ["전체 축척: 하란–세일 포함", "가나안 확대: 얍복강–세겜–벧엘"], help="전체 축척은 하란과 세일의 실제 거리감을 보여주고, 가나안 확대는 창 32–33장의 사건을 자세히 보여줍니다.")
    basemap = st.radio("배경 지도", ["아주 밝은 지도(추천)", "밝은 지도", "기본 지도", "지형 지도"], index=0)
    show_jacob_route = st.checkbox("야곱의 이동 경로", True)
    show_esau_route = st.checkbox("에서의 이동 방향(세일)", True)
    show_labels = st.checkbox("현대 지명 라벨 표시", True)
    show_bethel_note = st.checkbox("벧엘: 아직 미도달 강조", True)
    route_width = st.slider("경로 선 굵기", 4, 12, 8)
    marker_size_hint = st.caption("위치 포인트는 흰색 테두리+번호 원형 마커로 표시됩니다.")
    selected_type = st.multiselect("표시할 장소 유형", options=sorted(set(item["type"] for item in LOCATIONS)), default=sorted(set(item["type"] for item in LOCATIONS)))

    st.divider()
    st.subheader("거리감")
    st.metric("하란 → 벧엘 개념 경로", f"약 {route_distance(ROUTE_JACOB_FULL):,.0f} km")
    st.metric("만남 장소 → 세일", f"약 {route_distance(ROUTE_ESAU):,.0f} km")
    st.caption("직선/개념 경로 기반 근사값입니다.")

left, right = st.columns([1.35, 0.65], gap="large")

with left:
    if map_mode.startswith("전체"):
        center, zoom, active_jacob_route, bounds = [33.7, 36.9], 6, ROUTE_JACOB_FULL, [[30.15, 35.05], [37.05, 39.25]]
    else:
        center, zoom, active_jacob_route, bounds = [32.05, 35.45], 9, ROUTE_JACOB_CANAAN, [[31.80, 35.10], [32.35, 35.75]]

    if basemap == "아주 밝은 지도(추천)":
        m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
    elif basemap == "밝은 지도":
        m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
    elif basemap == "지형 지도":
        m = folium.Map(location=center, zoom_start=zoom, tiles="OpenTopoMap")
    else:
        m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")

    if basemap == "아주 밝은 지도(추천)":
        folium.TileLayer(
            tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
            attr="© OpenStreetMap contributors © CARTO",
            name="아주 밝은 배경",
            overlay=False,
            control=True,
        ).add_to(m)

    folium.TileLayer("CartoDB positron", name="밝은 지도").add_to(m)
    folium.TileLayer("OpenStreetMap", name="기본 지도").add_to(m)
    folium.TileLayer("OpenTopoMap", name="지형 지도").add_to(m)
    Fullscreen().add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    MeasureControl(primary_length_unit="kilometers").add_to(m)

    if show_jacob_route:
        AntPath(active_jacob_route, color="#5b21b6", weight=route_width + 3, opacity=0.25, delay=900, dash_array=[15, 25]).add_to(m)
        AntPath(active_jacob_route, color="#5b21b6", weight=route_width, opacity=0.95, delay=900, dash_array=[15, 25], tooltip="야곱의 이동 흐름").add_to(m)

    if show_esau_route:
        folium.PolyLine(ROUTE_ESAU, color="#ffffff", weight=route_width + 4, opacity=0.9, dash_array="10, 10").add_to(m)
        folium.PolyLine(ROUTE_ESAU, color="#dc2626", weight=route_width, opacity=0.95, dash_array="10, 10", tooltip="에서의 이동 방향: 남쪽 세일/에돔으로 돌아감").add_to(m)

    for loc in LOCATIONS:
        if map_mode.startswith("가나안") and loc["id"] == 1:
            continue
        if loc["type"] not in selected_type:
            continue
        add_number_marker(m, loc)
        if show_labels:
            add_label(m, loc)

    if show_bethel_note:
        folium.CircleMarker(location=[31.9410, 35.2330], radius=24, color="#ffffff", weight=5, fill=False).add_to(m)
        folium.CircleMarker(location=[31.9410, 35.2330], radius=22, color="#991b1b", weight=4, fill=True, fill_opacity=0.10, tooltip="벧엘: 하나님이 명령하신 목적지, 창 33장에서는 아직 미도달").add_to(m)

    folium.LayerControl(collapsed=True).add_to(m)
    m.fit_bounds(bounds)
    st_folium(m, width=None, height=700)

with right:
    st.subheader("📌 시점별 사건 순서")
    for event in EVENTS:
        with st.expander(f"{event['step']}. {event['title']} ({event['refs']})", expanded=event["step"] <= 3):
            st.write(event["text"])

    st.divider()
    st.subheader("🧭 위치 검증 요약")
    st.write("**밧단아람/하란**은 북쪽 튀르키예 Harran 일대입니다.")
    st.write("**세일**은 얍복강 근처가 아니라 훨씬 남쪽, 에돔 산지/Petra 일대입니다.")
    st.write("배경은 기본적으로 아주 밝게 설정해 경로와 포인트가 잘 보이도록 했습니다.")

    st.divider()
    st.subheader("장소별 표")
    df = pd.DataFrame(LOCATIONS)[["id", "name", "modern", "type", "refs"]]
    st.dataframe(df, hide_index=True, use_container_width=True)

st.divider()

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 얍복강")
    st.write("하나님과 씨름하며 야곱이 깨어지고 이스라엘로 변화되는 자리입니다.")
with c2:
    st.markdown("### 에서의 얼굴")
    st.write("야곱은 형의 얼굴에서 하나님의 얼굴을 본 것 같다고 고백합니다. 화해는 은혜의 결과입니다.")
with c3:
    st.markdown("### 벧엘")
    st.write("하나님을 만난 자리이자 다시 돌아가야 할 자리입니다. 창 33장에서는 아직 도달하지 못했습니다.")

st.warning("고대 지명 좌표는 학자별 비정 차이가 있습니다. 이 앱은 성경공부용 시각화이며, 정확한 고고학·역사지리 논증을 대체하지 않습니다.")
