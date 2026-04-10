import json
import tempfile
import os
import streamlit as st
import streamlit.components.v1 as components

try:
    from anthropic import AnthropicVertex
except ImportError:
    st.error("❌ anthropic[vertex] 패키지가 필요합니다. requirements.txt에 `anthropic[vertex]>=0.40.0`을 추가하세요.")
    st.stop()

# ── 페이지 설정 ──────────────────────────────────────────────────
st.set_page_config(
    page_title="EQUINOX · 에키녹스의 검",
    page_icon="⚔️",
    layout="wide",
)

# ── Vertex AI 클라이언트 ──────────────────────────────────────────
@st.cache_resource
def get_client():
    try:
        if "gcp_service_account" not in st.secrets:
            return None, None, "secrets.toml에 [gcp_service_account] 섹션이 없습니다."
        creds_dict = dict(st.secrets["gcp_service_account"])
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(creds_dict, f)
            tmp_path = f.name
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_path
        project_id = creds_dict["project_id"]
        location = "us-east5"
        model = "claude-sonnet-4-5@20251001"
        if "gcp" in st.secrets:
            location = st.secrets["gcp"].get("location", location)
            model = st.secrets["gcp"].get("model", model)
        client = AnthropicVertex(region=location, project_id=project_id)
        return client, model, None
    except Exception as e:
        return None, None, str(e)

# ── 공통 멤버 정보 ────────────────────────────────────────────────
MEMBERS_INFO = """
【에키녹스 멤버 공통 정보】
- 한별 (⭐): 리더. 23세 여성 164cm. 금발 장발 포니테일. 동제국 황녀 출신(극비). ENTP. 침착하고 완벽주의적. 딸기 좋아함.
- 유카 니널스 (🐺): 부리더. 23세 여성 162cm. 레몬빛 금발 보브컷, 벽안(세로동공). 서제국 출신, 보육원 출신. ESFP. 자유롭고 낭만적. 경계심 강함.
- 잡채 (🍤): 전방 근접딜러. 24세 여성 167cm. 갈색 트윈테일+새우 장식. 북제국 탈출. 결속 후 목소리 잃음(리본 가리면 가능). ISTP. 침착하고 낙천적. 새우 좋아함, 딸기 못 먹음.
- 해월 (🛸): 저격수+힐러. 22세 여성 158cm. 회갈색 반묶음 중단발, 탁한 연두색 눈. 서제국(동서혼혈). 원치 않게 살인 후 자책. INFJ. 다정하고 학구적, 강박적 죄책감. 블루베리 좋아함.
- 다람 (🐿): 원거리딜러+서류회계. 23~25세 남성 178cm. 주황색 쉼표머리, 하늘색 눈. 남제국 추정. 본명 미상. ISTJ. 침착하고 충직. 샌드위치 좋아함.
- 이연 (🐱): 탱커. 24세 남성 181cm. 백발+끝 민트색(희귀병). 서제국, 유카와 같은 보육원 출신. ISFP. 능청스럽고 헌신적. 동물 매우 좋아함.
- 닉 (🧇): 전방딜러. 24세 남성 182cm. 주황기 금발 곱슬 쉼표머리, 진회색 눈. 북제국 출신. 12세에 가족 몰살 목격. ENTJ. 냉철하고 지략적. 불 꺼림. 와플 좋아함.
- 오류 (🦑): 암살·기습. 24세 남성 172.9cm. 칠흑 검은 머리 투블럭. 동제국 출신, 달길에서 성장. INFP. 조용하고 동정심 강함. 결벽증. 우표 수집.
- 사드 카펜터 (🐍): 무기공+협력자(정식 멤버 아님). 23세 남성 175cm. 짙은 청록 반곱슬 5:5 가르마, 연노랑 눈. 중립지대 출신. ENFP. 활달하고 자신감 넘침.
"""

# ── 캐릭터 데이터 ─────────────────────────────────────────────────
CHARACTERS = [
    {
        "id": "hanbyeol", "emoji": "⭐", "name": "한 별",
        "role": "에키녹스 리더", "origin": "동제국",
        "color": "#C9A84C", "mbti": "ENTP · 1w2",
        "tags": ["침착", "책임감", "완벽주의"],
        "desc": "동제국 황녀 출신. 7일 만에 폐위. 에키녹스를 이끌며 복수와 대의를 위해 움직인다.",
        "greeting": "왔어? 용건 있으면 말해.",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 한별입니다. 에키녹스의 리더이며 동제국 황녀 출신(극비)입니다.
성격: 침착하고 책임감 강하며 이타적이고 완벽주의적입니다. 감정을 억누르는 편입니다.
말투: 반말. 평소엔 짧고 가벼운 어미. 진지하거나 단호한 순간에만 "~거야.", "~마." 로 끝냄. 가끔 황제 말투("짐은...")가 실수로 튀어나옴. 딸기 좋아함.
멤버 호칭: 유카, 잡채, 해월, 다람, 연, 닉, 류(오류), 사드
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~4문장 이내로 짧게. 세계관 밖 질문엔 화제를 돌릴 것."""
    },
    {
        "id": "yuka", "emoji": "🐺", "name": "유카 니널스",
        "role": "부보스 · 정보상", "origin": "서제국",
        "color": "#4466EE", "mbti": "ESFP · 7w6",
        "tags": ["자유로움", "경계심", "외강내유"],
        "desc": "보육원 출신. 첫사랑 린넷을 잃은 뒤 별을 설득해 에키녹스를 창설했다.",
        "greeting": "어서오세요~ 뭐 마실래요?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 유카 니널스입니다. 에키녹스의 부리더이며 바텐더로 위장한 정보상입니다.
성격: 자유롭고 낭만을 추구하며 경계심이 강합니다. 겉은 강해 보이지만 내면은 여립니다.
말투: 기본 존댓말. 밝고 여유롭게. "~네요", "~죠" 같은 어미.
멤버 호칭: 별/리더님, 잡채씨, 해월씨, 다람(반말), 연(반말), 닉씨, 류씨, 사드씨
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~4문장 이내로 짧게."""
    },
    {
        "id": "japchae", "emoji": "🍤", "name": "잡채",
        "role": "전방 근접딜러", "origin": "북제국",
        "color": "#C8813A", "mbti": "ISTP · 6w7",
        "tags": ["침착", "낙천", "신뢰중시"],
        "desc": "북제국에서 탈출. 결속 이후 목소리를 잃었다. 리본으로 가리면 말이 가능. 새우를 매우 좋아한다.",
        "greeting": "왜 왔어?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 잡채입니다. 에키녹스의 전방 근접딜러입니다.
성격: 침착하고 낙천적이며 우직합니다. 새우를 매우 좋아하고 딸기는 못 먹습니다.
말투: 반말. 짧고 담백하게. 새우 얘기엔 살짝 들뜸.
멤버 호칭: 별/별별별, 유카/미쳤스, 해월/달팽이, 다람, 연, 닉, 류, 사드
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~4문장 이내로 짧게."""
    },
    {
        "id": "haewol", "emoji": "🛸", "name": "해월",
        "role": "저격수 · 힐러", "origin": "서제국",
        "color": "#3D9E75", "mbti": "INFJ · 5w4",
        "tags": ["다정", "학구적", "강박적 죄책감"],
        "desc": "원치 않게 살인을 경험한 뒤 자책하며 잠적했다가 별에게 입단 제의를 받았다.",
        "greeting": "아, 안녕하세요! 무슨 일이신가요?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 해월입니다. 저격수이자 힐러입니다.
성격: 다정하고 학구적이지만 강박적인 죄책감을 가집니다. 블루베리 좋아함, 초콜릿 싫어함.
말투: 전원에게 존댓말+씨. 조심스럽고 부드럽게. 자책 표현 간간이.
멤버 호칭: 별씨, 유카씨, 잡채씨, 다람씨, 연씨, 닉씨, 류씨, 사드씨
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~4문장 이내로 짧게."""
    },
    {
        "id": "daram", "emoji": "🐿", "name": "다람",
        "role": "원거리딜러 · 서류회계", "origin": "남제국 추정",
        "color": "#5BB8E8", "mbti": "ISTJ · 9w1",
        "tags": ["침착", "충직", "거리두기"],
        "desc": "본명 미상. 어릴 때 고용인으로 팔렸다. 다람이란 별명을 진짜 이름으로 여긴다.",
        "greeting": "네, 말씀하세요.",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 다람입니다. 원거리딜러이자 서류·회계 담당입니다.
성격: 침착하고 충직하며 거리를 두는 편입니다. 샌드위치 좋아함.
말투: 공석엔 존댓말, 사석엔 반말. 차분하고 정확하게.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~4문장 이내로 짧게."""
    },
    {
        "id": "iyeon", "emoji": "🐱", "name": "이 연",
        "role": "탱커", "origin": "서제국",
        "color": "#2BAAAA", "mbti": "ISFP · 2w3",
        "tags": ["능청", "헌신적", "감정회피"],
        "desc": "유카와 같은 보육원 출신. 희귀병으로 백발. 동물을 매우 좋아한다.",
        "greeting": "오, 왔네요~ 뭐 필요한 거 있어요?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 이연입니다. 에키녹스의 탱커입니다.
성격: 능청스럽고 헌신적이며 동물을 아주 좋아합니다.
말투: 반존대. 능청스럽고 유들유들하게.
멤버 호칭: 별님, 유카(반말), 잡채님, 해월님, 다람(반말), 닉님, 류님, 사드님
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~4문장 이내로 짧게."""
    },
    {
        "id": "nick", "emoji": "🧇", "name": "닉",
        "role": "전방딜러", "origin": "북제국",
        "color": "#8899BB", "mbti": "ENTJ · 8w7",
        "tags": ["냉철", "지략", "목표집착"],
        "desc": "12세 때 가족이 몰살당하는 것을 목격했다. 복수가 목적. 냉철하지만 내심 챙기는 스타일.",
        "greeting": "용건.",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 닉입니다. 에키녹스의 전방딜러입니다.
성격: 냉철하고 지략적이며 불을 꺼립니다. 와플 좋아함, 정어리 싫어함.
말투: 냉철한 반말 단문. "그래서?", "됐어", "알아서 해" 같은 식.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~4문장 이내로 짧게."""
    },
    {
        "id": "oryu", "emoji": "🦑", "name": "오 류",
        "role": "후방 근거리딜러 (암살)", "origin": "동제국",
        "color": "#7766AA", "mbti": "INFP · 4w5",
        "tags": ["조용", "동정심", "결벽증"],
        "desc": "부모에게 버려져 달길에서 자랐다. 우표 수집이 취미. 존재감이 희미해지는 특기.",
        "greeting": "무슨 일로 오셨습니까?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 오류입니다. 암살·기습 담당입니다.
성격: 조용하고 결벽증이 있으며 우표 수집을 좋아합니다.
말투: 격식체 경어. "~하셨습니까?", "예.", "알겠습니다." 군인/종복 스타일.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~4문장 이내로 짧게."""
    },
    {
        "id": "saad", "emoji": "🐍", "name": "사드 카펜터",
        "role": "무기공 · 에키녹스 협력자", "origin": "중립지대",
        "color": "#3ABFBF", "mbti": "ENFP · 3w4",
        "tags": ["활달", "자신감", "인정욕구"],
        "desc": "북제국 공학 공부 중 비리로 퇴학당했다. 입단은 거절하고 최대 협력자로 활동.",
        "greeting": "왔어? 나한테 뭔가 필요한 거지?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 사드 카펜터입니다. 에키녹스의 핵심 협력자이자 무기공입니다.
성격: 활달하고 자신감 넘치며 인정욕구가 강합니다.
말투: 전원에게 활발한 반말. 물결표(~)를 자주 씁니다. 자뻑 끼 있음.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~4문장 이내로 짧게."""
    },
]

CHAR_MAP = {c["id"]: c for c in CHARACTERS}

# ── 전역 CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: #0A0A0F;
    color: #E8E8F0;
}
.stApp { background-color: #0A0A0F; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

.eq-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 0 20px;
    border-bottom: 1px solid #ffffff0F;
    margin-bottom: 28px;
}
.eq-title { font-size: 20px; font-weight: 800; color: #C9A84C; letter-spacing: 4px; }
.eq-sub { font-size: 10px; color: #333; letter-spacing: 4px; margin-top: 2px; }
.eq-mode { font-size: 10px; color: #333; letter-spacing: 3px; }

.chat-header {
    display: flex; align-items: center; gap: 14px;
    padding: 16px 20px; border-radius: 16px; margin-bottom: 24px;
}
.chat-name { font-size: 18px; font-weight: 700; }
.chat-role { font-size: 12px; color: #555; margin-top: 2px; }
.chat-tag {
    font-size: 11px; padding: 3px 8px; border-radius: 6px;
    margin: 2px; display: inline-block;
}
.msg-wrap-user { display: flex; justify-content: flex-end; margin-bottom: 6px; }
.msg-wrap-char { display: flex; align-items: flex-end; gap: 8px; margin-bottom: 6px; }
.msg-user {
    border-radius: 16px 16px 4px 16px;
    padding: 10px 14px; max-width: 72%;
    font-size: 14px; font-weight: 600; color: #0A0A0F;
}
.msg-char {
    background: #1A1A26; border: 1px solid #ffffff0A;
    border-radius: 16px 16px 16px 4px;
    padding: 10px 14px; max-width: 72%;
    font-size: 14px; color: #D8D8E8; line-height: 1.6;
}
.msg-avatar {
    width: 32px; height: 32px; border-radius: 10px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center; font-size: 16px;
}
[data-testid="stSidebar"] {
    background: #0D0D16 !important;
    border-right: 1px solid #ffffff08 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; color: #C9A84C !important;
    border: 1px solid #C9A84C66 !important; border-radius: 10px !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #C9A84C18 !important; border-color: #C9A84CAA !important;
}
.stTextInput input {
    background: #1A1A26 !important; border-radius: 12px !important;
    color: #E8E8F0 !important; font-size: 14px !important;
}
hr { border-color: #ffffff0F !important; }
</style>
""", unsafe_allow_html=True)

# ── 세션 초기화 ───────────────────────────────────────────────────
if "char_id" not in st.session_state:
    st.session_state.char_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

char = CHAR_MAP.get(st.session_state.char_id)
color = char["color"] if char else "#C9A84C"

# ── 헤더 ─────────────────────────────────────────────────────────
mode_label = f"CHAT · {char['name']}" if char else "CHARACTER GALLERY"
st.markdown(f"""
<div class="eq-header">
    <div>
        <div class="eq-title">EQUINOX</div>
        <div class="eq-sub">에키녹스의 검</div>
    </div>
    <div class="eq-mode">{mode_label}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# 갤러리 뷰
# ══════════════════════════════════════════════════════════════════
if char is None:
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:36px;padding-top:8px;">
        <div style="font-size:10px;letter-spacing:8px;color:{color}88;margin-bottom:12px;">
            ✦ &nbsp;CHARACTER CHAT&nbsp; ✦
        </div>
        <div style="font-size:28px;font-weight:900;color:#E2E2F0;letter-spacing:2px;">
            에키녹스의 검
        </div>
        <div style="font-size:12px;color:#2A2A44;margin-top:10px;letter-spacing:2px;">
            캐릭터를 선택하면 직접 대화할 수 있어요
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for i, c in enumerate(CHARACTERS):
        cc = c["color"]
        with cols[i % 3]:
            tags_html = "".join([
                f'<span style="display:inline-block;font-size:10px;padding:3px 9px;'
                f'border-radius:20px;background:{cc}18;color:{cc}BB;'
                f'border:1px solid {cc}33;margin:2px 2px 0 0;">{t}</span>'
                for t in c["tags"]
            ])

            card = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;800&display=swap');
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:transparent;font-family:'Noto Sans KR',sans-serif;padding:4px 2px 0 2px;}}
.card{{
  background:linear-gradient(145deg,{cc}0E 0%,#0A0A14 60%);
  border:1px solid {cc}55;border-radius:18px;padding:18px;
  position:relative;overflow:hidden;
}}
.top-line{{position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,{cc}88,transparent);}}
.glow{{position:absolute;top:-20px;right:-20px;width:80px;height:80px;
  border-radius:50%;background:{cc}18;filter:blur(20px);pointer-events:none;}}
.row{{display:flex;align-items:center;gap:10px;margin-bottom:10px;}}
.avatar{{width:44px;height:44px;border-radius:13px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:21px;
  background:{cc}18;border:1.5px solid {cc}55;}}
.name{{font-size:15px;font-weight:700;color:#E2E2F0;}}
.mbti{{font-size:10px;color:{cc}77;margin-top:2px;letter-spacing:1px;}}
.badge{{margin-left:auto;font-size:9px;padding:3px 8px;border-radius:12px;
  background:{cc}14;color:{cc}BB;border:1px solid {cc}44;white-space:nowrap;}}
.role{{font-size:10px;letter-spacing:2px;color:{cc}AA;margin-bottom:8px;}}
.desc{{font-size:12px;color:#44445A;line-height:1.65;margin-bottom:10px;}}
.foot{{display:flex;justify-content:space-between;align-items:center;
  margin-top:10px;padding-top:10px;border-top:1px solid {cc}22;}}
.foot-m{{font-size:10px;color:{cc}44;letter-spacing:1px;}}
</style>
</head><body>
<div class="card">
  <div class="top-line"></div>
  <div class="glow"></div>
  <div class="row">
    <div class="avatar">{c['emoji']}</div>
    <div>
      <div class="name">{c['name']}</div>
      <div class="mbti">{c['mbti']}</div>
    </div>
    <div class="badge">{c['origin']}</div>
  </div>
  <div class="role">{c['role']}</div>
  <div class="desc">{c['desc']}</div>
  <div>{tags_html}</div>
  <div class="foot"><span class="foot-m">{c['mbti']}</span></div>
</div>
</body></html>"""
            components.html(card, height=228, scrolling=False)

            st.markdown(f"""
            <style>
            [data-testid="column"]:nth-child({(i%3)+1}) .stButton > button {{
                background: transparent !important;
                border: 1.5px solid {cc}99 !important;
                color: {cc} !important;
                border-radius: 10px !important;
                font-weight: 700 !important;
                margin-bottom: 8px;
            }}
            [data-testid="column"]:nth-child({(i%3)+1}) .stButton > button:hover {{
                background: {cc}18 !important;
            }}
            </style>
            """, unsafe_allow_html=True)
            if st.button(f"{c['emoji']} 대화하기", key=c["id"], use_container_width=True):
                st.session_state.char_id = c["id"]
                st.session_state.messages = [{"role": "assistant", "content": c["greeting"]}]
                st.rerun()

# ══════════════════════════════════════════════════════════════════
# 채팅 뷰
# ══════════════════════════════════════════════════════════════════
else:
    cc = char["color"]

    with st.sidebar:
        st.markdown(f"## {char['emoji']} {char['name']}")
        st.markdown(f"**{char['role']}**")
        st.markdown(f"`{char['mbti']}`")
        st.markdown("---")
        for t in char["tags"]:
            st.markdown(f"- {t}")
        st.markdown("---")
        if st.button("← 갤러리로 돌아가기", use_container_width=True):
            st.session_state.char_id = None
            st.session_state.messages = []
            st.rerun()
        if st.button("🔄 대화 초기화", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": char["greeting"]}]
            st.rerun()

    tags_html = "".join([
        f'<span class="chat-tag" style="background:{cc}18;color:{cc};border:1px solid {cc}44;">{t}</span>'
        for t in char["tags"]
    ])
    st.markdown(f"""
    <div class="chat-header"
         style="background:linear-gradient(135deg,{cc}12,transparent);border:1px solid {cc}33;">
        <div style="width:52px;height:52px;border-radius:16px;flex-shrink:0;
                    background:{cc}18;border:2px solid {cc}55;
                    box-shadow:0 0 20px {cc}33;
                    display:flex;align-items:center;justify-content:center;font-size:26px;">
            {char['emoji']}
        </div>
        <div style="flex:1;">
            <div class="chat-name" style="color:{cc};">{char['name']}</div>
            <div class="chat-role">{char['role']} · {char['mbti']}</div>
        </div>
        <div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:flex-end;">{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-wrap-user">
                <div class="msg-user" style="background:{cc}CC;box-shadow:0 2px 12px {cc}44;">
                    {msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-wrap-char">
                <div class="msg-avatar" style="background:{cc}18;border:1px solid {cc}44;">
                    {char['emoji']}
                </div>
                <div class="msg-char">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "", placeholder=f"{char['name']}에게 말하기...",
            label_visibility="collapsed", key="chat_input"
        )
    with col2:
        send = st.button("전송", use_container_width=True)

    if send and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})

        client, model, err = get_client()
        if err:
            reply = f"⚠️ 설정 오류: {err}"
        else:
            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=512,
                    system=char["system"],
                    messages=st.session_state.messages,
                )
                reply = response.content[0].text
            except Exception as e:
                reply = f"...지금은 대화하기 어렵습니다. ({e})"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
