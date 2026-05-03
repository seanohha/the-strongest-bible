import streamlit as st
import pandas as pd
import folium
from folium.plugins import AntPath
from streamlit_folium import st_folium

st.set_page_config(
    page_title="야곱의 여정 인터랙티브 성경지도",
    page_icon="🗺️",
    layout="wide",
)

# ------------------------------------------------------------
# 데이터
# 좌표는 고대 지명 비정에 따른 교육용 근사값입니다.
# ------------------------------------------------------------
LOCATIONS = [
    {
        "id": 1,
        "name": "밧단아람 / 하란",
        "modern": "Harran, Türkiye",
        "lat": 36.8670,
        "lon": 39.0310,
        "type": "출발지",
        "refs": "창 31:1–3, 33:18",
        "summary": "야곱이 라반의 집에서 20년가량 머문 뒤, 하나님의 명령을 따라 고향으로 향해 출발한 곳입니다.",
        "theology": "하나님의 인도는 도망자의 긴 세월도 약속의 여정으로 바꾸십니다.",
    },
    {
        "id": 2,
        "name": "얍복강",
        "modern": "Zarqa River, Jordan",
        "lat": 32.1830,
        "lon": 35.6160,
        "type": "전환점",
        "refs": "창 32:3–32, 호 12:3–4",
        "summary": "야곱이 에서를 두려워하며 사자를 보내고, 가족과 재산을 나누고, 밤에는 홀로 남아 하나님과 씨름한 곳입니다.",
        "theology": "진짜 문제는 에서가 아니라 하나님 앞에서 깨어지지 않은 야곱 자신이었습니다.",
    },
    {
        "id": 3,
        "name": "에서와의 만남 장소",
        "modern": "요단 동편 / 얍복강 서쪽 추정",
        "lat": 32.1400,
        "lon": 35.5750,
        "type": "화해",
        "refs": "창 33:1–11",
        "summary": "야곱이 일곱 번 땅에 엎드리며 나아갔고, 에서가 달려와 안고 입맞추며 서로 운 장소입니다.",
        "theology": "하나님과의 화해가 사람과의 화해로 이어졌습니다. 야곱은 에서의 얼굴에서 하나님의 얼굴을 본 것 같다고 고백합니다.",
    },
    {
        "id": 4,
        "name": "세일",
        "modern": "Edom / southern Jordan, Petra region",
        "lat": 30.3285,
        "lon": 35.4444,
        "type": "에서의 방향",
        "refs": "창 33:12–16",
        "summary": "에서가 돌아간 방향입니다. 야곱은 함께 가겠다고 말했지만 실제로는 세일로 가지 않았습니다.",
        "theology": "화해는 이루어졌지만, 야곱의 여정은 여전히 하나님의 목적지로 계속되어야 했습니다.",
    },
    {
        "id": 5,
        "name": "숙곳",
        "modern": "Deir Alla vicinity, Jordan",
        "lat": 32.2000,
        "lon": 35.6200,
        "type": "멈춤",
        "refs": "창 33:17",
        "summary": "야곱이 집을 짓고 가축을 위해 우릿간을 세운 곳입니다. 이름은 ‘장막/초막’을 뜻합니다.",
        "theology": "위기가 지나가자 야곱은 다시 머물기 시작합니다. 은혜 이후에도 순종은 계속되어야 합니다.",
    },
    {
        "id": 6,
        "name": "세겜",
        "modern": "Nablus, Palestine / West Bank",
        "lat": 32.2211,
        "lon": 35.2544,
        "type": "부분 순종",
        "refs": "창 33:18–20",
        "summary": "야곱이 밧단아람에서부터 평안히 가나안 땅 세겜에 이르러 장막을 치고 밭을 사며 제단을 쌓은 곳입니다.",
        "theology": "제단을 쌓고 ‘엘엘로헤이스라엘’이라 고백했지만, 아직 벧엘까지는 가지 않았습니다.",
    },
    {
        "id": 7,
        "name": "벧엘",
        "modern": "Beitin, Palestine / West Bank",
        "lat": 31.9410,
        "lon": 35.2330,
        "type": "가야 할 목적지",
        "refs": "창 28:10–22, 31:13, 35:1",
        "summary": "야곱이 처음 하나님을 만난 장소이며, 하나님께서 돌아가라고 명하신 목적지입니다. 창 33장에서는 아직 도달하지 못했습니다.",
        "theology": "벧엘은 완전한 순종의 자리입니다. 하나님을 만난 사람은 결국 하나님이 부르신 자리로 돌아가야 합니다.",
    },
]

EVENTS = [
    {"step": 1, "title": "밧단아람/하란 출발", "refs": "창 31:1–3", "text": "하나님의 명령을 듣고 라반의 집을 떠나 고향으로 향함."},
    {"step": 2, "title": "얍복강 도착 전 두려움", "refs": "창 32:3–9", "text": "에서가 400명을 데리고 온다는 소식에 두려워하고, 무리를 두 떼로 나누고 기도함."},
    {"step": 3, "title": "예물 준비와 보냄", "refs": "창 32:13–21", "text": "에서의 감정을 풀기 위해 예물을 여러 떼로 나누어 먼저 보냄."},
    {"step": 4, "title": "얍복강 사건", "refs": "창 32:22–32", "text": "홀로 남은 야곱이 하나님과 씨름하고, 이름이 이스라엘로 바뀜."},
    {"step": 5, "title": "에서와의 만남", "refs": "창 33:1–11", "text": "야곱이 일곱 번 절하며 나아가고, 에서는 달려와 안고 입맞추며 화해함."},
    {"step": 6, "title": "에서은 세일로 돌아감", "refs": "창 33:12–16", "text": "에서는 함께 가자고 하지만 야곱은 사양하고, 에서는 세일로 돌아감."},
    {"step": 7, "title": "야곱은 숙곳에 머묾", "refs": "창 33:17", "text": "야곱은 숙곳에 이르러 집과 우릿간을 지으며 머무름."},
    {"step": 8, "title": "세겜 도착과 제단", "refs": "창 33:18–20", "text": "밧단아람에서부터 평안히 세겜에 이르러 밭을 사고 제단을 쌓음."},
    {"step": 9, "title": "벧엘 — 아직 미도달", "refs": "창 28:10–22, 31:13", "text": "하나님이 명령하신 목적지는 벧엘이지만 창 33장에서는 아직 이르지 못함."},
]

ROUTE_JACOB = [
    (36.8670, 39.0310),  # Haran
    (32.1830, 35.6160),  # Jabbok
    (32.1400, 35.5750),  # meeting
    (32.2000, 35.6200),  # Succoth
    (32.2211, 35.2544),  # Shechem
    (31.9410, 35.2330),  # Bethel destination marker
]

ROUTE_ESAU = [
    (32.1400, 35.5750),
    (30.3285, 35.4444),
]

TYPE_COLORS = {
    "출발지": "blue",
    "전환점": "purple",
    "화해": "red",
    "에서의 방향": "orange",
    "멈춤": "cadetblue",
    "부분 순종": "green",
    "가야 할 목적지": "darkred",
}

st.title("🗺️ 야곱의 여정 인터랙티브 성경지도")
st.caption("창세기 28:10–33:20 | 하나님과의 만남에서 에서와의 화해, 그리고 아직 남은 벧엘의 부르심까지")

with st.sidebar:
    st.header("지도 설정")
    show_jacob_route = st.checkbox("야곱의 실제 이동 경로", True)
    show_esau_route = st.checkbox("에서의 이동 방향(세일)", True)
    show_bethel_note = st.checkbox("벧엘: 아직 미도달 강조", True)
    selected_type = st.multiselect(
        "표시할 장소 유형",
        options=sorted(set(item["type"] for item in LOCATIONS)),
        default=sorted(set(item["type"] for item in LOCATIONS)),
    )

    st.divider()
    st.subheader("핵심 메시지")
    st.write("사람과의 화해는 하나님과의 화해에서 시작됩니다.")
    st.write("그러나 화해 이후에도 완전한 순종, 곧 벧엘로 가는 길은 계속됩니다.")

left, right = st.columns([1.35, 0.65], gap="large")

with left:
    m = folium.Map(location=[32.2, 35.65], zoom_start=7, tiles="OpenStreetMap")

    if show_jacob_route:
        AntPath(
            ROUTE_JACOB,
            color="#5b2aa0",
            weight=5,
            delay=900,
            dash_array=[15, 25],
            tooltip="야곱의 실제 이동 흐름: 밧단아람/하란 → 얍복강 → 에서 만남 → 숙곳 → 세겜 → 벧엘(목적지)",
        ).add_to(m)

    if show_esau_route:
        folium.PolyLine(
            ROUTE_ESAU,
            color="#d94b2b",
            weight=4,
            dash_array="10, 10",
            tooltip="에서의 이동 방향: 세일(에돔)로 돌아감",
        ).add_to(m)

    for loc in LOCATIONS:
        if loc["type"] not in selected_type:
            continue
        popup_html = f"""
        <div style='width: 280px'>
            <h4>{loc['id']}. {loc['name']}</h4>
            <b>현재 위치:</b> {loc['modern']}<br>
            <b>유형:</b> {loc['type']}<br>
            <b>본문:</b> {loc['refs']}<br><br>
            <b>사건:</b><br>{loc['summary']}<br><br>
            <b>신학적 의미:</b><br>{loc['theology']}
        </div>
        """
        folium.Marker(
            [loc["lat"], loc["lon"]],
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=f"{loc['id']}. {loc['name']} ({loc['modern']})",
            icon=folium.Icon(color=TYPE_COLORS.get(loc["type"], "blue"), icon="info-sign"),
        ).add_to(m)

    if show_bethel_note:
        folium.CircleMarker(
            location=[31.9410, 35.2330],
            radius=18,
            color="#8b0000",
            fill=True,
            fill_opacity=0.15,
            tooltip="벧엘: 하나님이 명령하신 목적지, 창 33장에서는 아직 미도달",
        ).add_to(m)

    st_folium(m, width=None, height=680)

with right:
    st.subheader("📌 시점별 사건 순서")
    for event in EVENTS:
        with st.expander(f"{event['step']}. {event['title']} ({event['refs']})", expanded=event["step"] <= 3):
            st.write(event["text"])

    st.divider()
    st.subheader("🧭 장소별 신앙 의미")
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

st.info(
    "지명과 좌표는 고대 지명 비정에 근거한 교육용 근사값입니다. "
    "세겜은 현재 나블루스(Nablus), 벧엘은 베이틴(Beitin) 인근으로 주로 비정됩니다."
)
