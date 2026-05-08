import math

import folium
import pandas as pd
import streamlit as st
from folium.plugins import AntPath, Fullscreen, MeasureControl, MiniMap
from streamlit_folium import st_folium

st.set_page_config(page_title="인터랙티브 성경지도", page_icon="🗺️", layout="wide")

TYPE_HEX = {
    "출발지": "#2563eb", "전환점": "#7c3aed", "화해": "#dc2626", "에서의 방향": "#ea580c",
    "멈춤": "#0891b2", "부분 순종": "#16a34a", "가야 할 목적지": "#991b1b",
    "언약 가문": "#2563eb", "긴장": "#f59e0b", "배신": "#dc2626", "무역로": "#7c3aed", "섭리": "#16a34a",
}
BASEMAPS = {
    "아주 밝은 지도(추천)": {"tiles": "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png", "attr": "© OpenStreetMap contributors © CARTO", "name": "아주 밝은 지도"},
    "밝은 지도": {"tiles": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", "attr": "© OpenStreetMap contributors © CARTO", "name": "밝은 지도"},
    "기본 지도": {"tiles": "OpenStreetMap", "attr": None, "name": "기본 지도"},
    "지형 지도": {"tiles": "OpenTopoMap", "attr": None, "name": "지형 지도"},
}

JACOB_LOCATIONS = [
    {"id": 1, "name": "밧단아람 / 하란", "modern": "Harran, Türkiye", "lat": 36.8670, "lon": 39.0310, "type": "출발지", "refs": "창 31:1–3, 33:18", "summary": "야곱이 라반의 집에서 약 20년을 머문 뒤 고향으로 향해 출발한 곳입니다.", "theology": "도망자의 긴 세월도 하나님의 약속 안에서는 귀환의 여정이 됩니다."},
    {"id": 2, "name": "얍복강", "modern": "Zarqa River, Jordan", "lat": 32.1830, "lon": 35.6160, "type": "전환점", "refs": "창 32:3–32", "summary": "야곱이 하나님과 씨름한 곳입니다.", "theology": "진짜 문제는 에서가 아니라 하나님 앞에서 깨어지지 않은 야곱 자신이었습니다."},
    {"id": 3, "name": "에서와의 만남", "modern": "얍복강 서쪽/요단 동편 추정", "lat": 32.1250, "lon": 35.5600, "type": "화해", "refs": "창 33:1–11", "summary": "야곱과 에서가 화해한 장소로 추정됩니다.", "theology": "하나님과의 화해가 사람과의 화해로 이어졌습니다."},
    {"id": 4, "name": "세일", "modern": "Edom / Petra–Showbak region", "lat": 30.3285, "lon": 35.4444, "type": "에서의 방향", "refs": "창 33:12–16", "summary": "에서가 돌아간 남쪽 에돔 산지입니다.", "theology": "화해는 이루어졌지만 야곱의 부르심은 벧엘을 향해 계속됩니다."},
    {"id": 5, "name": "숙곳", "modern": "Tell Deir Alla vicinity, Jordan", "lat": 32.1900, "lon": 35.6200, "type": "멈춤", "refs": "창 33:17", "summary": "야곱이 집과 우릿간을 지으며 머문 곳입니다.", "theology": "은혜 이후에도 순종은 계속되어야 합니다."},
    {"id": 6, "name": "세겜", "modern": "Nablus, Palestine / West Bank", "lat": 32.2211, "lon": 35.2544, "type": "부분 순종", "refs": "창 33:18–20", "summary": "야곱이 제단을 쌓은 곳입니다.", "theology": "예배는 드렸지만 아직 벧엘까지는 가지 않았습니다."},
    {"id": 7, "name": "벧엘", "modern": "Beitin, Palestine / West Bank", "lat": 31.9410, "lon": 35.2330, "type": "가야 할 목적지", "refs": "창 28:10–22, 31:13", "summary": "야곱이 처음 하나님을 만난 곳이자 돌아가야 할 목적지입니다.", "theology": "벧엘은 완전한 순종의 자리입니다."},
]
JACOB_EVENTS = [
    {"step": 1, "loc_id": 1, "title": "밧단아람/하란 출발", "refs": "창 31:1–3", "text": "하나님의 명령을 듣고 라반의 집을 떠납니다.", "verse": "네 조상의 땅 네 족속에게로 돌아가라.", "question": "내가 떠나야 할 익숙한 자리는 무엇입니까?", "emotion": "부르심", "christ": "하나님이 먼저 약속의 길을 여십니다."},
    {"step": 2, "loc_id": 2, "title": "얍복강 도착 전 두려움", "refs": "창 32:3–9", "text": "야곱은 에서가 400명을 데리고 온다는 소식에 두려워합니다.", "verse": "야곱이 심히 두렵고 답답하여...", "question": "약속을 알면서도 두려운 문제는 무엇입니까?", "emotion": "두려움", "christ": "두려움 속에서도 하나님은 언약을 지키십니다."},
    {"step": 3, "loc_id": 2, "title": "예물 준비", "refs": "창 32:13–21", "text": "야곱은 예물로 형의 감정을 풀려 합니다.", "verse": "예물로 형의 감정을 푼 후에...", "question": "나는 계산으로만 관계를 해결하려 합니까?", "emotion": "계산", "christ": "은혜는 거래가 아니라 주어지는 것입니다."},
    {"step": 4, "loc_id": 2, "title": "얍복강 씨름", "refs": "창 32:22–32", "text": "하나님과 씨름하며 야곱이 이스라엘로 바뀝니다.", "verse": "네 이름을 이스라엘이라 부를 것이니.", "question": "하나님 앞에서 꺾여야 할 것은 무엇입니까?", "emotion": "깨어짐", "christ": "참 변화는 하나님과의 만남에서 시작됩니다."},
    {"step": 5, "loc_id": 3, "title": "에서와의 만남", "refs": "창 33:1–11", "text": "에서가 달려와 야곱을 안고 서로 웁니다.", "verse": "하나님의 얼굴을 본 것 같사오며.", "question": "화해의 은혜를 경험한 적이 있습니까?", "emotion": "화해", "christ": "그리스도 안에서 원수 된 관계가 회복됩니다."},
    {"step": 6, "loc_id": 4, "title": "에서는 세일로", "refs": "창 33:16", "text": "에서는 남쪽 세일로 돌아갑니다.", "verse": "에서는 세일로 돌아가고.", "question": "화해 후에도 각자의 길이 다를 수 있음을 받아들입니까?", "emotion": "분리", "christ": "화해는 집착이 아니라 자유를 줍니다."},
    {"step": 7, "loc_id": 5, "title": "야곱은 숙곳에 머묾", "refs": "창 33:17", "text": "야곱은 숙곳에 집과 우릿간을 짓습니다.", "verse": "자기를 위하여 집을 짓고...", "question": "내가 안주한 숙곳은 어디입니까?", "emotion": "안주", "christ": "은혜 후에도 순종의 길은 계속됩니다."},
    {"step": 8, "loc_id": 6, "title": "세겜 제단", "refs": "창 33:18–20", "text": "야곱은 세겜에서 제단을 쌓습니다.", "verse": "엘엘로헤이스라엘이라 불렀더라.", "question": "예배는 있으나 순종이 지연된 영역은 무엇입니까?", "emotion": "부분 순종", "christ": "예배는 목적지가 아니라 순종으로 이어져야 합니다."},
    {"step": 9, "loc_id": 7, "title": "벧엘 — 아직 미도달", "refs": "창 31:13", "text": "하나님이 부르신 벧엘에는 아직 도착하지 못합니다.", "verse": "나는 벧엘의 하나님이라.", "question": "하나님이 부르시는 벧엘은 무엇입니까?", "emotion": "부르심", "christ": "하나님은 끝까지 약속의 자리로 부르십니다."},
]
JACOB_ROUTES = {
    "전체 축척: 하란–세일 포함": [(36.8670, 39.0310), (36.8, 38.0), (35.9, 37.7), (34.8, 36.5), (33.5, 36.3), (32.183, 35.616), (32.125, 35.56), (32.19, 35.62), (32.2211, 35.2544), (31.941, 35.233)],
    "가나안 확대: 얍복강–세겜–벧엘": [(32.183, 35.616), (32.125, 35.56), (32.19, 35.62), (32.2211, 35.2544), (31.941, 35.233)],
}
JACOB_ESAU_ROUTE = [(32.125, 35.56), (31.3, 35.48), (30.3285, 35.4444)]

JOSEPH_LOCATIONS = [
    {"id": 1, "name": "헤브론", "modern": "Hebron, West Bank", "lat": 31.5326, "lon": 35.0998, "type": "언약 가문", "refs": "창 37:14", "summary": "야곱이 요셉을 형들에게 보내는 출발지입니다.", "theology": "언약 가정 안에서도 죄와 분열이 드러납니다."},
    {"id": 2, "name": "세겜", "modern": "Nablus, Palestine / West Bank", "lat": 32.2211, "lon": 35.2544, "type": "긴장", "refs": "창 37:12–14", "summary": "형들이 양을 치러 간 첫 목적지입니다.", "theology": "세겜은 야곱 가문에게 폭력과 상처의 기억이 있는 장소입니다."},
    {"id": 3, "name": "도단", "modern": "Tel Dothan, West Bank", "lat": 32.4133, "lon": 35.2386, "type": "배신", "refs": "창 37:17–28", "summary": "요셉이 형들을 만나고 구덩이에 던져져 팔린 실제 사건의 중심지입니다.", "theology": "인간의 배신이 하나님의 섭리의 통로로 바뀌는 전환점입니다."},
    {"id": 4, "name": "길르앗", "modern": "Gilead region, Jordan", "lat": 32.3000, "lon": 35.8500, "type": "무역로", "refs": "창 37:25", "summary": "향품·유향·몰약을 싣고 애굽으로 가던 상인들이 온 방향입니다.", "theology": "우연처럼 보이는 무역로도 하나님의 계획 안에 있습니다."},
    {"id": 5, "name": "애굽", "modern": "Egypt / Nile Delta direction", "lat": 30.0444, "lon": 31.2357, "type": "섭리", "refs": "창 37:36", "summary": "요셉이 보디발에게 팔려 들어간 곳입니다.", "theology": "죽음 같은 내려감이 장차 구원의 자리로 이어집니다."},
]
JOSEPH_EVENTS = [
    {"step": 1, "loc_id": 1, "title": "요셉이 보냄 받음", "refs": "창 37:12–14", "text": "야곱은 형들과 양 떼의 안부를 살피라고 요셉을 보냅니다.", "verse": "가서 네 형들과 양 떼가 다 잘 있는지를 보고 돌아와 내게 말하라.", "question": "나는 맡겨진 작은 순종을 가볍게 여기지는 않습니까?", "emotion": "순종", "christ": "아버지에게 보냄 받은 아들로서 요셉은 그리스도를 예표합니다."},
    {"step": 2, "loc_id": 2, "title": "세겜에서 도단으로", "refs": "창 37:15–17", "text": "요셉은 세겜에서 형들을 찾지 못하고 도단으로 향합니다.", "verse": "그들이 여기서 떠났느니라... 도단으로 가자 하는 말을 들었노라.", "question": "하나님의 섭리 안에서 예상과 다른 길로 인도된 경험이 있습니까?", "emotion": "추적", "christ": "잃은 자를 찾으시는 그리스도의 길이 떠오릅니다."},
    {"step": 3, "loc_id": 3, "title": "살인 모의", "refs": "창 37:18–20", "text": "형들은 요셉을 멀리서 보고 죽이기를 꾀합니다.", "verse": "꿈 꾸는 자가 오는도다... 그의 꿈이 어떻게 되는지를 우리가 볼 것이니라.", "question": "내 안의 시기와 미움이 하나님의 뜻을 거부하게 하지는 않습니까?", "emotion": "시기·증오", "christ": "의인을 미워하고 제거하려는 인간의 죄는 예수님의 수난을 예표합니다."},
    {"step": 4, "loc_id": 3, "title": "구덩이에 던져짐", "refs": "창 37:23–24", "text": "형들은 요셉의 채색옷을 벗기고 빈 구덩이에 던집니다.", "verse": "그의 채색옷을 벗기고 그를 잡아 구덩이에 던지니.", "question": "타인의 고통에 무감각해진 적은 없습니까?", "emotion": "폭력·무감각", "christ": "옷 벗김과 낮아짐은 십자가 수치를 미리 보여줍니다."},
    {"step": 5, "loc_id": 4, "title": "상인들이 지나감", "refs": "창 37:25", "text": "길르앗에서 온 상인들이 애굽으로 내려갑니다.", "verse": "향품과 유향과 몰약을 싣고 애굽으로 내려가는지라.", "question": "우연처럼 보였지만 나중에 섭리였음을 깨달은 일이 있습니까?", "emotion": "우연처럼 보이는 섭리", "christ": "하나님은 인간의 악을 넘어 구원의 길을 준비하십니다."},
    {"step": 6, "loc_id": 3, "title": "은 이십에 팔림", "refs": "창 37:26–28", "text": "유다의 제안으로 요셉은 은 이십에 팔립니다.", "verse": "은 이십에 그를 이스마엘 사람들에게 팔매.", "question": "내가 손해 보지 않으려는 계산이 누군가를 해치지는 않습니까?", "emotion": "배신·거래", "christ": "요셉의 팔림은 은에 팔리신 예수님을 예표합니다."},
    {"step": 7, "loc_id": 1, "title": "피 묻은 채색옷", "refs": "창 37:31–35", "text": "형들은 염소 피를 채색옷에 묻혀 야곱을 속입니다.", "verse": "아버지 아들의 옷인가 보소서.", "question": "죄를 감추기 위해 더 큰 거짓을 만든 적은 없습니까?", "emotion": "거짓·애통", "christ": "죄는 한 사람만이 아니라 공동체 전체를 울게 합니다."},
    {"step": 8, "loc_id": 5, "title": "애굽으로 팔려감", "refs": "창 37:36", "text": "요셉은 애굽에서 보디발에게 팔립니다.", "verse": "그 미디안 사람들은 그를 애굽에서... 보디발에게 팔았더라.", "question": "하나님이 보이지 않아도 일하고 계심을 믿을 수 있습니까?", "emotion": "침묵 속 섭리", "christ": "낮아짐 이후 높아짐을 통해 많은 사람을 살리는 구원자의 길이 시작됩니다."},
]
JOSEPH_ROUTE = [(31.5326, 35.0998), (32.2211, 35.2544), (32.4133, 35.2386)]
JOSEPH_TRADE_ROUTE = [(32.3, 35.85), (32.4133, 35.2386), (31.5326, 34.9), (30.6, 33.0), (30.0444, 31.2357)]


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def route_distance(points):
    return sum(haversine_km(a[0], a[1], b[0], b[1]) for a, b in zip(points[:-1], points[1:]))


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


def add_number_marker(m, loc, active=False):
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


def draw_map(center, zoom, bounds, basemap, locations, current_loc, show_context, visible_ids, base_route=None, active_route=None, trade_route=None, route_width=8, show_bethel=False):
    m = folium.Map(location=center, zoom_start=zoom, tiles=None, prefer_canvas=True)
    add_selected_basemap(m, basemap)
    add_optional_basemaps(m, basemap)
    Fullscreen().add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    MeasureControl(primary_length_unit="kilometers").add_to(m)

    if show_context and base_route and len(base_route) >= 2:
        folium.PolyLine(base_route, color="#9ca3af", weight=3, opacity=.35, dash_array="4, 8").add_to(m)
    if active_route and len(active_route) >= 2:
        AntPath(active_route, color="#5b21b6", weight=route_width + 3, opacity=.20, delay=900, dash_array=[15, 25]).add_to(m)
        AntPath(active_route, color="#5b21b6", weight=route_width, opacity=.98, delay=900, dash_array=[15, 25], tooltip="현재 시점까지 이동 흐름").add_to(m)
    if trade_route and len(trade_route) >= 2:
        folium.PolyLine(trade_route, color="#ffffff", weight=route_width + 4, opacity=.9, dash_array="10, 10").add_to(m)
        folium.PolyLine(trade_route, color="#16a34a", weight=route_width, opacity=.95, dash_array="10, 10", tooltip="섭리/무역로 흐름").add_to(m)

    for loc in locations:
        if not show_context and loc["id"] not in visible_ids:
            continue
        add_number_marker(m, loc, active=(loc["id"] == current_loc["id"]))

    if show_bethel:
        folium.CircleMarker(location=[31.9410, 35.2330], radius=22, color="#991b1b", weight=4, fill=True, fill_opacity=.10).add_to(m)

    folium.LayerControl(collapsed=True).add_to(m)
    m.fit_bounds(bounds)
    return m


def route_cut(route, step, cuts):
    return route[:cuts.get(step, len(route))]


def run_study(study_key, basemap, route_width, show_context):
    if study_key == "야곱의 귀환과 화해 (창 33장)":
        st.title("🗺️ 야곱의 여정 인터랙티브 성경지도")
        st.caption("창세기 28:10–33:20 | 시간·공간·신학 레이어")
        map_mode = st.sidebar.radio("지도 모드", list(JACOB_ROUTES.keys()))
        step = st.sidebar.slider("시점 선택", 1, len(JACOB_EVENTS), len(JACOB_EVENTS))
        show_esau = st.sidebar.checkbox("에서의 이동 방향 표시", True)
        show_bethel = st.sidebar.checkbox("벧엘 강조", True)
        events, locs = JACOB_EVENTS, JACOB_LOCATIONS
        current = events[step - 1]
        current_loc = next(l for l in locs if l["id"] == current["loc_id"])
        full_mode = map_mode.startswith("전체")
        route = JACOB_ROUTES[map_mode]
        cuts = {1: 1, 2: 6, 3: 6, 4: 6, 5: 7, 6: 7, 7: 8, 8: 9, 9: 10} if full_mode else {1: 0, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 4, 9: 5}
        active = route_cut(route, step, cuts)
        trade = JACOB_ESAU_ROUTE if show_esau and step >= 6 else None
        center, zoom, bounds = ([33.7, 36.9], 6, [[30.15, 35.05], [37.05, 39.25]]) if full_mode else ([32.05, 35.45], 9, [[31.80, 35.10], [32.35, 35.75]])
        visible_ids = {e["loc_id"] for e in events[:step]}
        m = draw_map(center, zoom, bounds, basemap, locs, current_loc, show_context, visible_ids, route, active, trade, route_width, show_bethel and step >= 8)
        return m, events, locs, current

    st.title("🧥 피로 적신 채색옷 — 요셉 사건 지도")
    st.caption("창세기 37:18–36 | 지리 + 감정 + 섭리 + 그리스도 예표")
    map_mode = st.sidebar.radio("지도 모드", ["전체: 헤브론–도단–애굽", "도단 확대: 세겜–도단"])
    step = st.sidebar.slider("시점 선택", 1, len(JOSEPH_EVENTS), len(JOSEPH_EVENTS))
    show_trade = st.sidebar.checkbox("섭리/무역로 레이어 표시", True)
    events, locs = JOSEPH_EVENTS, JOSEPH_LOCATIONS
    current = events[step - 1]
    current_loc = next(l for l in locs if l["id"] == current["loc_id"])
    if map_mode.startswith("전체"):
        center, zoom, bounds = [31.7, 34.2], 6, [[29.7, 30.7], [32.7, 36.1]]
        base_route = JOSEPH_ROUTE
        trade_route = JOSEPH_TRADE_ROUTE if show_trade and step >= 5 else None
    else:
        center, zoom, bounds = [32.25, 35.24], 10, [[31.95, 35.0], [32.55, 35.45]]
        base_route = JOSEPH_ROUTE
        trade_route = [(32.3, 35.85), (32.4133, 35.2386)] if show_trade and step >= 5 else None
    cuts = {1: 1, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 1, 8: 3}
    active = route_cut(JOSEPH_ROUTE, step, cuts)
    visible_ids = {e["loc_id"] for e in events[:step]}
    m = draw_map(center, zoom, bounds, basemap, locs, current_loc, show_context, visible_ids, base_route, active, trade_route, route_width)
    return m, events, locs, current


with st.sidebar:
    st.header("본문 선택")
    study = st.selectbox("나눔지/본문", ["야곱의 귀환과 화해 (창 33장)", "요셉과 피 묻은 채색옷 (창 37장)"])
    basemap = st.radio("배경 지도", list(BASEMAPS.keys()), index=0)
    show_context = st.checkbox("전체 여정 배경으로 함께 보기", True)
    route_width = st.slider("경로 선 굵기", 4, 12, 8)

m, events, locs, current = run_study(study, basemap, route_width, show_context)

left, right = st.columns([1.35, .65], gap="large")
with left:
    st_folium(m, width=None, height=700, key=f"map-{study}-{current['step']}-{basemap}-{show_context}-{route_width}")

with right:
    st.subheader(f"⏱️ 현재 시점 {current['step']}/{len(events)}")
    st.markdown(f"### {current['title']}")
    st.caption(current["refs"])
    st.write(current["text"])
    st.markdown("#### 📖 핵심 본문")
    st.info(current["verse"])
    st.markdown("#### 💔 감정 레이어")
    st.warning(current.get("emotion", ""))
    st.markdown("#### ✝️ 그리스도 예표 / 신학")
    st.info(current.get("christ", ""))
    st.markdown("#### 💬 나눔 질문")
    st.success(current["question"])
    st.divider()
    st.subheader("📌 전체 사건 순서")
    for event in events:
        prefix = "👉 " if event["step"] == current["step"] else ""
        with st.expander(f"{prefix}{event['step']}. {event['title']} ({event['refs']})", expanded=event["step"] == current["step"]):
            st.write(event["text"])
            st.caption(event["question"])
    st.divider()
    st.subheader("장소별 표")
    st.dataframe(pd.DataFrame(locs)[["id", "name", "modern", "type", "refs"]], hide_index=True, use_container_width=True)

st.divider()
if study.startswith("요셉"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 💔 감정 흐름")
        st.write("편애 → 시기 → 미움 → 폭력 → 거짓 → 애통")
    with c2:
        st.markdown("### 🟢 섭리 흐름")
        st.write("구덩이와 애굽행은 실패처럼 보이지만, 장차 많은 생명을 살리는 길이 됩니다.")
    with c3:
        st.markdown("### ✝️ 그리스도 예표")
        st.write("요셉은 미움받고 팔리고 낮아지지만, 훗날 구원의 통로가 됩니다.")
else:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 얍복강")
        st.write("하나님과 씨름하며 야곱이 깨어지는 자리입니다.")
    with c2:
        st.markdown("### 에서의 얼굴")
        st.write("화해는 하나님의 은혜의 결과입니다.")
    with c3:
        st.markdown("### 벧엘")
        st.write("하나님을 만난 자리이자 다시 돌아가야 할 자리입니다.")

st.warning("고대 지명 좌표는 학자별 비정 차이가 있습니다. 이 앱은 성경공부용 시각화이며, 정확한 고고학·역사지리 논증을 대체하지 않습니다.")
