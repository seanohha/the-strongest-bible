import json
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from folium.plugins import AntPath, Fullscreen, MeasureControl, MiniMap
from streamlit_folium import st_folium

st.set_page_config(page_title="인터랙티브 성경지도", page_icon="🗺️", layout="wide")

VISITOR_FILE = Path("visitor_count.json")
if not VISITOR_FILE.exists():
    VISITOR_FILE.write_text(json.dumps({"count": 0}), encoding="utf-8")
try:
    visitor_data = json.loads(VISITOR_FILE.read_text(encoding="utf-8"))
except Exception:
    visitor_data = {"count": 0}
if "visitor_incremented" not in st.session_state:
    visitor_data["count"] = int(visitor_data.get("count", 0)) + 1
    VISITOR_FILE.write_text(json.dumps(visitor_data), encoding="utf-8")
    st.session_state["visitor_incremented"] = True
VISITOR_COUNT = int(visitor_data.get("count", 0))

BASEMAPS = {
    "아주 밝은 지도(추천)": {"tiles": "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png", "attr": "© OpenStreetMap contributors © CARTO"},
    "밝은 지도": {"tiles": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", "attr": "© OpenStreetMap contributors © CARTO"},
    "기본 지도": {"tiles": "OpenStreetMap", "attr": None},
    "지형 지도": {"tiles": "OpenTopoMap", "attr": None},
}
TYPE_HEX = {"출발지":"#2563eb","전환점":"#7c3aed","화해":"#dc2626","에서의 방향":"#ea580c","멈춤":"#0891b2","부분 순종":"#16a34a","목적지":"#991b1b","긴장":"#f59e0b","배신":"#dc2626","무역로":"#7c3aed","섭리":"#16a34a","교회 문제":"#dc2626","성장":"#16a34a","터":"#111827","심판":"#f59e0b","도시 배경":"#2563eb"}

STUDY_OPTIONS = [
    "야곱의 귀환과 화해 (창 33장)",
    "요셉과 피 묻은 채색옷 (창 37장)",
    "하나님의 마음 — 요셉의 용서와 화해 (창 45장)",
    "지혜로운 건축자 (고전 3장)",
]
LATEST_STUDY = "지혜로운 건축자 (고전 3장)"

DATA = {
"야곱의 귀환과 화해 (창 33장)": {
"title":"🗺️ 야곱의 귀환과 화해","caption":"창세기 28:10–33:20 | 시간·공간·신학 레이어","center":[32.05,35.45],"zoom":8,"bounds":[[31.75,35.05],[32.4,35.8]],
"locations":[
{"id":1,"name":"밧단아람/하란","modern":"Harran, Türkiye","lat":36.867,"lon":39.031,"type":"출발지","refs":"창 31:1–3","summary":"야곱이 라반의 집에서 떠난 곳입니다.","theology":"귀환의 여정은 하나님의 약속으로 시작됩니다."},
{"id":2,"name":"얍복강","modern":"Zarqa River, Jordan","lat":32.183,"lon":35.616,"type":"전환점","refs":"창 32:22–32","summary":"야곱이 하나님과 씨름한 곳입니다.","theology":"하나님 앞에서 깨어지는 자리입니다."},
{"id":3,"name":"에서와의 만남","modern":"요단 동편 추정","lat":32.125,"lon":35.56,"type":"화해","refs":"창 33:1–11","summary":"야곱과 에서가 화해한 장소로 추정됩니다.","theology":"하나님과의 화해가 사람과의 화해로 이어집니다."},
{"id":4,"name":"세일","modern":"Edom / southern Jordan","lat":30.3285,"lon":35.4444,"type":"에서의 방향","refs":"창 33:16","summary":"에서가 돌아간 에돔 산지입니다.","theology":"화해 후에도 각자의 길이 있습니다."},
{"id":5,"name":"숙곳","modern":"Tell Deir Alla vicinity","lat":32.19,"lon":35.62,"type":"멈춤","refs":"창 33:17","summary":"야곱이 집과 우릿간을 지은 곳입니다.","theology":"은혜 이후에도 순종은 계속되어야 합니다."},
{"id":6,"name":"세겜","modern":"Nablus, West Bank","lat":32.2211,"lon":35.2544,"type":"부분 순종","refs":"창 33:18–20","summary":"야곱이 제단을 쌓은 곳입니다.","theology":"예배는 드렸지만 아직 벧엘까지 가지 않았습니다."},
{"id":7,"name":"벧엘","modern":"Beitin, West Bank","lat":31.941,"lon":35.233,"type":"목적지","refs":"창 28:10–22, 31:13","summary":"하나님을 처음 만난 자리입니다.","theology":"완전한 순종의 목적지입니다."}],
"events":[
{"step":1,"loc_id":1,"title":"밧단아람/하란 출발","refs":"창 31:1–3","text":"하나님의 명령을 듣고 라반의 집을 떠납니다.","verse":"네 조상의 땅 네 족속에게로 돌아가라.","emotion":"부르심","christ":"하나님이 먼저 약속의 길을 여십니다.","question":"내가 떠나야 할 익숙한 자리는 무엇입니까?"},
{"step":2,"loc_id":2,"title":"얍복강의 두려움과 씨름","refs":"창 32장","text":"야곱은 두려움 속에서 하나님과 씨름하며 이스라엘로 변화됩니다.","verse":"네 이름을 이스라엘이라 부를 것이니.","emotion":"두려움과 깨어짐","christ":"참 변화는 하나님과의 만남에서 시작됩니다.","question":"하나님 앞에서 꺾여야 할 것은 무엇입니까?"},
{"step":3,"loc_id":3,"title":"에서와의 만남","refs":"창 33:1–11","text":"에서는 야곱을 안고 서로 웁니다.","verse":"하나님의 얼굴을 본 것 같사오며.","emotion":"화해","christ":"그리스도 안에서 원수 된 관계가 회복됩니다.","question":"화해의 은혜를 경험한 적이 있습니까?"},
{"step":4,"loc_id":4,"title":"에서는 세일로","refs":"창 33:16","text":"에서는 세일로 돌아갑니다.","verse":"에서는 세일로 돌아가고.","emotion":"분리","christ":"화해는 집착이 아니라 자유를 줍니다.","question":"화해 후 각자의 길을 받아들입니까?"},
{"step":5,"loc_id":5,"title":"숙곳에 머묾","refs":"창 33:17","text":"야곱은 숙곳에 집을 짓습니다.","verse":"자기를 위하여 집을 짓고.","emotion":"안주","christ":"은혜 후에도 순종의 길은 계속됩니다.","question":"내가 안주한 숙곳은 어디입니까?"},
{"step":6,"loc_id":6,"title":"세겜 제단","refs":"창 33:18–20","text":"야곱은 세겜에서 제단을 쌓습니다.","verse":"엘엘로헤이스라엘이라 불렀더라.","emotion":"부분 순종","christ":"예배는 순종으로 이어져야 합니다.","question":"예배는 있으나 순종이 지연된 영역은 무엇입니까?"},
{"step":7,"loc_id":7,"title":"벧엘 — 아직 미도달","refs":"창 31:13","text":"하나님이 부르신 벧엘에 아직 이르지 못했습니다.","verse":"나는 벧엘의 하나님이라.","emotion":"부르심","christ":"하나님은 끝까지 약속의 자리로 부르십니다.","question":"하나님이 부르시는 벧엘은 무엇입니까?"}],
"route":[(36.867,39.031),(32.183,35.616),(32.125,35.56),(32.19,35.62),(32.2211,35.2544),(31.941,35.233)],"cards":[("얍복강","하나님과 씨름하며 깨어지는 자리입니다."),("에서의 얼굴","화해는 하나님의 은혜의 결과입니다."),("벧엘","하나님을 만난 자리이자 다시 돌아가야 할 자리입니다.")]},

"요셉과 피 묻은 채색옷 (창 37장)": {
"title":"🧥 피로 적신 채색옷 — 요셉 사건","caption":"창세기 37:18–36 | 지리 + 감정 + 섭리 + 그리스도 예표","center":[31.7,34.2],"zoom":6,"bounds":[[29.7,30.7],[32.7,36.1]],
"locations":[
{"id":1,"name":"헤브론","modern":"Hebron, West Bank","lat":31.5326,"lon":35.0998,"type":"출발지","refs":"창 37:14","summary":"야곱이 요셉을 보낸 출발지입니다.","theology":"언약 가정 안에서도 죄와 분열이 드러납니다."},
{"id":2,"name":"세겜","modern":"Nablus, West Bank","lat":32.2211,"lon":35.2544,"type":"긴장","refs":"창 37:12–17","summary":"형들이 양을 치러 간 첫 목적지입니다.","theology":"상처와 폭력의 기억이 있는 장소입니다."},
{"id":3,"name":"도단","modern":"Tel Dothan, West Bank","lat":32.4133,"lon":35.2386,"type":"배신","refs":"창 37:18–28","summary":"요셉이 구덩이에 던져지고 팔린 중심지입니다.","theology":"인간의 배신이 하나님의 섭리의 통로가 됩니다."},
{"id":4,"name":"길르앗","modern":"Gilead region, Jordan","lat":32.3,"lon":35.85,"type":"무역로","refs":"창 37:25","summary":"상인들이 온 방향입니다.","theology":"우연처럼 보이는 무역로도 하나님의 계획 안에 있습니다."},
{"id":5,"name":"애굽","modern":"Egypt","lat":30.0444,"lon":31.2357,"type":"섭리","refs":"창 37:36","summary":"요셉이 팔려간 곳입니다.","theology":"죽음 같은 내려감이 구원의 자리로 이어집니다."}],
"events":[
{"step":1,"loc_id":1,"title":"요셉이 보냄 받음","refs":"창 37:12–14","text":"요셉은 형들의 안부를 살피러 보냄 받습니다.","verse":"가서 네 형들과 양 떼가 잘 있는지를 보고 오라.","emotion":"순종","christ":"아버지께 보냄 받은 아들로서 그리스도를 예표합니다.","question":"맡겨진 작은 순종을 가볍게 여기지는 않습니까?"},
{"step":2,"loc_id":2,"title":"세겜에서 도단으로","refs":"창 37:15–17","text":"요셉은 형들을 찾아 도단으로 향합니다.","verse":"도단으로 가자 하는 말을 들었노라.","emotion":"추적","christ":"잃은 자를 찾으시는 그리스도의 길이 떠오릅니다.","question":"예상과 다른 길로 인도된 경험이 있습니까?"},
{"step":3,"loc_id":3,"title":"살인 모의와 구덩이","refs":"창 37:18–24","text":"형들은 요셉을 미워하여 구덩이에 던집니다.","verse":"꿈 꾸는 자가 오는도다.","emotion":"시기와 폭력","christ":"의인을 미워하는 인간의 죄는 예수님의 수난을 예표합니다.","question":"내 안의 시기와 미움이 하나님의 뜻을 거부하게 하지는 않습니까?"},
{"step":4,"loc_id":4,"title":"상인들이 지나감","refs":"창 37:25","text":"길르앗에서 온 상인들이 애굽으로 갑니다.","verse":"애굽으로 내려가는지라.","emotion":"우연처럼 보이는 섭리","christ":"하나님은 인간의 악을 넘어 구원의 길을 준비하십니다.","question":"나중에 섭리였음을 깨달은 일이 있습니까?"},
{"step":5,"loc_id":3,"title":"은 이십에 팔림","refs":"창 37:26–28","text":"요셉은 은 이십에 팔립니다.","verse":"은 이십에 그를 팔매.","emotion":"배신과 거래","christ":"요셉의 팔림은 은에 팔리신 예수님을 예표합니다.","question":"내 계산이 누군가를 해치지는 않습니까?"},
{"step":6,"loc_id":5,"title":"애굽으로 팔려감","refs":"창 37:36","text":"요셉은 애굽에서 보디발에게 팔립니다.","verse":"보디발에게 팔았더라.","emotion":"침묵 속 섭리","christ":"낮아짐 이후 많은 사람을 살리는 구원자의 길이 시작됩니다.","question":"하나님이 보이지 않아도 일하고 계심을 믿습니까?"}],
"route":[(31.5326,35.0998),(32.2211,35.2544),(32.4133,35.2386),(32.3,35.85),(30.0444,31.2357)],"cards":[("감정 흐름","편애 → 시기 → 미움 → 폭력 → 거짓 → 애통"),("섭리 흐름","구덩이와 애굽행은 장차 생명을 살리는 길이 됩니다."),("그리스도 예표","요셉은 미움받고 팔리고 낮아지지만 훗날 구원의 통로가 됩니다.")]},

"하나님의 마음 — 요셉의 용서와 화해 (창 45장)": {
"title":"🕊️ 하나님의 마음 — 요셉의 용서와 화해","caption":"창세기 45:1–15 | 용서 · 섭리 · 생명 보존 · 그리스도 예표","center":[30.8,32.5],"zoom":6,"bounds":[[29.7,30.7],[32.0,35.5]],
"locations":[
{"id":1,"name":"가나안","modern":"Hebron / Canaan","lat":31.5326,"lon":35.0998,"type":"출발지","refs":"창 42–44","summary":"야곱의 가족이 기근 속에 있던 곳입니다.","theology":"기근은 감추어진 죄와 상처를 드러내는 회복의 시작이 되었습니다."},
{"id":2,"name":"애굽","modern":"Egypt","lat":30.0444,"lon":31.2357,"type":"섭리","refs":"창 45:1–15","summary":"요셉이 형들에게 자신을 밝히고 용서한 장소입니다.","theology":"형들이 판 곳이 아니라 하나님이 먼저 보내신 구원의 무대입니다."},
{"id":3,"name":"고센","modern":"Eastern Nile Delta","lat":30.58,"lon":31.50,"type":"화해","refs":"창 45:10–11","summary":"요셉이 가족을 초청한 생명 보존의 장소입니다.","theology":"하나님은 언약 공동체 전체의 생명을 보존하십니다."}],
"events":[
{"step":1,"loc_id":1,"title":"기근과 애굽행","refs":"창 42–44","text":"가나안의 기근 때문에 형들은 애굽으로 양식을 구하러 내려옵니다.","verse":"기근 속에서 형들은 애굽으로 내려가고 요셉 앞에 엎드립니다.","emotion":"두려움과 필요","christ":"인간의 필요는 참 생명의 공급자이신 그리스도께로 이끕니다.","question":"내 삶의 결핍이 하나님께 나아가는 통로가 된 적이 있습니까?"},
{"step":2,"loc_id":2,"title":"유다의 변화 확인","refs":"창 44:19–34","text":"유다는 베냐민을 위해 자신이 대신 종이 되겠다고 청원합니다.","verse":"주의 종으로 그 아이를 대신하여 머물러 있게 하소서.","emotion":"회개와 책임","christ":"유다의 대속적 태도는 그리스도의 대속을 희미하게 보여줍니다.","question":"나는 과거의 잘못을 회피합니까, 책임을 지려 합니까?"},
{"step":3,"loc_id":2,"title":"요셉의 눈물","refs":"창 45:1–2","text":"요셉은 더 이상 정을 억제하지 못하고 큰 소리로 웁니다.","verse":"요셉이 큰 소리로 우니.","emotion":"상처와 사랑의 폭발","christ":"예수님도 죄인을 긍휼히 여기시는 주님이십니다.","question":"상처받은 자리에서도 하나님의 긍휼을 품을 수 있습니까?"},
{"step":4,"loc_id":2,"title":"나는 요셉이라","refs":"창 45:3–4","text":"요셉은 형들에게 자신의 정체를 밝힙니다.","verse":"나는 당신들의 아우 요셉이니.","emotion":"충격과 두려움","christ":"복음 앞에서 죄가 드러나지만 은혜가 가까이 오라 부릅니다.","question":"내 죄가 드러날 때 은혜 앞으로 나아갑니까?"},
{"step":5,"loc_id":2,"title":"하나님의 보내심","refs":"창 45:5–8","text":"요셉은 하나님이 생명을 구원하려 자신을 먼저 보내셨다고 고백합니다.","verse":"나를 이리로 보낸 이는 당신들이 아니요 하나님이시라.","emotion":"용서와 섭리의 확신","christ":"십자가는 인간의 악을 구원으로 바꾸신 사건입니다.","question":"고난 속에서 하나님이 무엇을 이루시는지 바라볼 수 있습니까?"},
{"step":6,"loc_id":3,"title":"고센으로 초청","refs":"창 45:9–13","text":"요셉은 가족 전체를 고센으로 데려오라고 합니다.","verse":"고센 땅에 머물며 나와 가깝게 하소서.","emotion":"초청과 보호","christ":"그리스도는 자기 백성을 가까이 부르시고 보호하십니다.","question":"내 자원은 보상입니까, 누군가를 살리기 위한 사명입니까?"},
{"step":7,"loc_id":2,"title":"입맞춤과 대화의 회복","refs":"창 45:14–15","text":"요셉은 형들을 안고 울며, 형들은 그제서야 요셉과 말합니다.","verse":"형들이 그제서야 요셉과 말하니라.","emotion":"화해와 회복","christ":"복음은 원수 된 자들을 그리스도 안에서 화목하게 합니다.","question":"이번 주 내가 먼저 화해의 손길을 내밀 사람은 누구입니까?"}],
"route":[(31.5326,35.0998),(30.0444,31.2357),(30.58,31.50)],"cards":[("유다의 변화","요셉을 팔던 유다가 이제는 베냐민을 위해 자신을 내어놓습니다."),("요셉의 용서","요셉은 형들의 죄보다 크신 하나님의 섭리를 바라봅니다."),("생명 보존","하나님은 요셉을 먼저 보내셔서 언약의 후손을 보존하십니다.")]},

"지혜로운 건축자 (고전 3장)": {
"title":"🏗️ 지혜로운 건축자","caption":"고린도전서 3:1–15 | 미성숙 · 분열 · 사역자의 역할 · 그리스도라는 터 · 불의 시험","center":[37.906,22.879],"zoom":15,"bounds":[[37.900,22.870],[37.912,22.888]],
"locations":[
{"id":1,"name":"고린도","modern":"Corinth, Greece","lat":37.906,"lon":22.879,"type":"도시 배경","refs":"고전 3:1–15","summary":"번성한 상업·항구 도시였지만 우상숭배와 타락이 공존했습니다.","theology":"세상의 가치관이 교회 안에 들어오면 미성숙과 분열이 생깁니다."},
{"id":2,"name":"교회 공동체","modern":"Corinthian Church","lat":37.9068,"lon":22.882,"type":"교회 문제","refs":"고전 3:1–4","summary":"바울파·아볼로파로 나뉘어 시기와 분쟁을 드러냈습니다.","theology":"은사가 많아도 그리스도 중심이 아니면 어린아이에 머뭅니다."},
{"id":3,"name":"밭과 집","modern":"God's field/building","lat":37.9085,"lon":22.875,"type":"성장","refs":"고전 3:6–9","summary":"심고 물 주는 이는 사역자이지만 자라게 하시는 분은 하나님입니다.","theology":"교회는 하나님의 밭이요 하나님의 집입니다."},
{"id":4,"name":"터: 예수 그리스도","modern":"Foundation","lat":37.9045,"lon":22.8765,"type":"터","refs":"고전 3:10–11","summary":"교회의 유일한 터는 예수 그리스도입니다.","theology":"교회는 사람, 부서, 훈련이 아니라 그리스도 위에 세워집니다."},
{"id":5,"name":"불의 시험","modern":"Day of testing","lat":37.9028,"lon":22.8835,"type":"심판","refs":"고전 3:12–15","summary":"각 사람이 무엇으로 교회를 세웠는지 불로 드러납니다.","theology":"말씀과 그리스도 위에 세운 공적만 남습니다."}],
"events":[
{"step":1,"loc_id":1,"title":"고린도의 배경","refs":"관점얻기","text":"고린도는 번성했지만 우상숭배와 타락이 만연했고 교회는 여러 문제를 겪었습니다.","verse":"복음을 받은 지 오래되었지만 여전히 미성숙에 머물렀습니다.","emotion":"혼합과 혼란","christ":"복음은 세상의 가치관을 그리스도 중심으로 새롭게 합니다.","question":"내 신앙 안에 세상의 비교 의식이 들어와 있지는 않습니까?"},
{"step":2,"loc_id":2,"title":"어린아이 같은 신앙","refs":"고전 3:1–2","text":"바울은 그들을 그리스도 안에서 어린아이처럼 대한다고 말합니다.","verse":"내가 너희를 젖으로 먹이고 밥으로 아니하였노니.","emotion":"미성숙","christ":"그리스도의 마음이 없으면 지식과 은사가 있어도 어린아이입니다.","question":"나는 말씀의 단단한 음식을 감당할 만큼 성숙해지고 있습니까?"},
{"step":3,"loc_id":2,"title":"시기와 분쟁","refs":"고전 3:3–4","text":"고린도 교회는 사람을 따라 바울파와 아볼로파로 나뉘었습니다.","verse":"너희 가운데 시기와 분쟁이 있으니.","emotion":"비교와 분열","christ":"사람을 자랑하면 몸이 찢어지지만 그리스도를 붙들면 하나 됩니다.","question":"특정 사람, 부서, 훈련을 자랑하며 판단한 적이 있습니까?"},
{"step":4,"loc_id":3,"title":"심고 물 주는 사역자","refs":"고전 3:5–9","text":"바울은 심고 아볼로는 물을 주었으나 자라게 하시는 이는 하나님뿐입니다.","verse":"오직 하나님께서 자라나게 하셨나니.","emotion":"겸손한 섬김","christ":"사역자는 주인이 아니라 그리스도의 일꾼입니다.","question":"나는 종의 자리에서 섬기고 있습니까?"},
{"step":5,"loc_id":4,"title":"유일한 터","refs":"고전 3:10–11","text":"바울은 교회의 유일한 터가 예수 그리스도라고 말합니다.","verse":"이 터는 곧 예수 그리스도라.","emotion":"본질 회복","christ":"교회의 기초와 머리는 예수 그리스도입니다.","question":"내 공동체의 실제 중심은 예수님입니까?"},
{"step":6,"loc_id":5,"title":"불로 드러나는 공적","refs":"고전 3:12–15","text":"금·은·보석인지 나무·풀·짚인지는 그 날에 불로 드러납니다.","verse":"그 불이 각 사람의 공적을 시험할 것임이라.","emotion":"두려운 점검","christ":"영원히 남는 것은 말씀과 그리스도 위에 세운 삶입니다.","question":"이번 주 그리스도 위에 남는 공적을 세우기 위해 무엇을 하겠습니까?"}],
"route":[(37.906,22.879),(37.9068,22.882),(37.9085,22.875),(37.9045,22.8765),(37.9028,22.8835)],"cards":[("자라게 하시는 하나님","사역자는 심고 물을 줄 뿐, 자라게 하시는 분은 하나님입니다."),("유일한 터","교회의 유일한 기초는 예수 그리스도입니다."),("불의 시험","무엇으로 교회를 세웠는지가 드러납니다.")]}
}


def add_basemap(m, name):
    cfg = BASEMAPS[name]
    kwargs = {"tiles": cfg["tiles"], "name": name, "overlay": False, "control": False}
    if cfg["attr"]:
        kwargs["attr"] = cfg["attr"]
    folium.TileLayer(**kwargs).add_to(m)


def popup_html(loc):
    return f"<div style='width:300px'><h4>{loc['id']}. {loc['name']}</h4><b>현재 위치/개념:</b> {loc['modern']}<br><b>유형:</b> {loc['type']}<br><b>본문:</b> {loc['refs']}<br><br><b>내용:</b><br>{loc['summary']}<br><br><b>신학적 의미:</b><br>{loc['theology']}</div>"


def add_marker(m, loc, active=False):
    color = TYPE_HEX.get(loc["type"], "#333")
    size = 44 if active else 34
    html = f"<div style='width:{size}px;height:{size}px;border-radius:50%;background:{color};color:white;border:4px solid white;box-shadow:0 3px 12px rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:{17 if active else 15}px'>{loc['id']}</div>"
    folium.Marker([loc["lat"], loc["lon"]], popup=folium.Popup(popup_html(loc), max_width=340), tooltip=f"{loc['id']}. {loc['name']} ({loc['type']})", icon=folium.DivIcon(html=html, class_name="clean-number-marker", icon_size=(size,size), icon_anchor=(size//2,size//2))).add_to(m)


def draw_map(study_data, step, basemap, show_context, route_width):
    events, locs = study_data["events"], study_data["locations"]
    current = events[step-1]
    current_loc = next(l for l in locs if l["id"] == current["loc_id"])
    m = folium.Map(location=study_data["center"], zoom_start=study_data["zoom"], tiles=None, prefer_canvas=True)
    add_basemap(m, basemap)
    Fullscreen().add_to(m); MiniMap(toggle_display=True).add_to(m); MeasureControl(primary_length_unit="kilometers").add_to(m)
    route = study_data["route"]
    if show_context and len(route) > 1:
        folium.PolyLine(route, color="#9ca3af", weight=3, opacity=.35, dash_array="4,8").add_to(m)
    active = route[:max(2, min(step+1, len(route)))]
    if len(active) > 1:
        AntPath(active, color="#5b21b6", weight=route_width, opacity=.95, delay=900, dash_array=[15,25], tooltip="현재 시점까지 흐름").add_to(m)
    visible_ids = {e["loc_id"] for e in events[:step]}
    for loc in locs:
        if show_context or loc["id"] in visible_ids:
            add_marker(m, loc, active=(loc["id"] == current_loc["id"]))
    folium.LayerControl(collapsed=True).add_to(m)
    m.fit_bounds(study_data["bounds"])
    return m, current, locs, events

with st.sidebar:
    st.markdown("## 📖 최신 질문지")
    st.info("고린도전서 3:1–15 — 지혜로운 건축자")
    st.markdown("## 👥 방문자 수")
    st.success(f"{VISITOR_COUNT:,} 명")
    st.header("본문 선택")
    study = st.selectbox("나눔지/본문", STUDY_OPTIONS, index=STUDY_OPTIONS.index(LATEST_STUDY))
    basemap = st.radio("배경 지도", list(BASEMAPS.keys()), index=0)
    show_context = st.checkbox("전체 흐름 배경으로 함께 보기", True)
    route_width = st.slider("경로 선 굵기", 4, 12, 8)
    step = st.slider("시점 선택", 1, len(DATA[study]["events"]), len(DATA[study]["events"]))

study_data = DATA[study]
st.title(study_data["title"])
st.caption(study_data["caption"])
m, current, locs, events = draw_map(study_data, step, basemap, show_context, route_width)

left, right = st.columns([1.35, .65], gap="large")
with left:
    st_folium(m, width=None, height=700, key=f"map-{study}-{step}-{basemap}-{show_context}-{route_width}")
with right:
    st.subheader(f"⏱️ 현재 시점 {current['step']}/{len(events)}")
    st.markdown(f"### {current['title']}")
    st.caption(current["refs"])
    st.write(current["text"])
    st.markdown("#### 📖 핵심 본문")
    st.info(current["verse"])
    st.markdown("#### 💔 상태/감정 레이어")
    st.warning(current.get("emotion", ""))
    st.markdown("#### ✝️ 복음 연결 / 신학")
    st.info(current.get("christ", ""))
    st.markdown("#### 💬 나눔 질문")
    st.success(current["question"])
    st.divider()
    st.subheader("📌 전체 흐름")
    for event in events:
        prefix = "👉 " if event["step"] == current["step"] else ""
        with st.expander(f"{prefix}{event['step']}. {event['title']} ({event['refs']})", expanded=event["step"] == current["step"]):
            st.write(event["text"]); st.caption(event["question"])
    st.divider()
    st.subheader("장소/개념 표")
    st.dataframe(pd.DataFrame(locs)[["id","name","modern","type","refs"]], hide_index=True, use_container_width=True)

st.divider()
c1, c2, c3 = st.columns(3)
for col, (title, body) in zip([c1,c2,c3], study_data["cards"]):
    with col:
        st.markdown(f"### {title}")
        st.write(body)

st.warning("고대 지명 좌표는 학자별 비정 차이가 있습니다. 일부 지도 마커는 본문 흐름을 설명하기 위한 개념적 배치입니다.")
