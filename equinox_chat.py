import json
import tempfile
import os
import streamlit as st
from anthropic import AnthropicVertex

# ── 페이지 설정 ──────────────────────────────────────
st.set_page_config(
    page_title="EQUINOX · 에키녹스의 검",
    page_icon="⚔️",
    layout="centered",
)

# ── 스타일 ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: #08080F;
    color: #E8E8F0;
}
.stApp { background-color: #08080F; }

/* 헤더 */
.eq-header {
    text-align: center;
    padding: 16px 0 8px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 24px;
}
.eq-logo {
    font-size: 32px; font-weight: 900;
    letter-spacing: 6px; color: #C9A84C;
}
.eq-sub {
    font-size: 11px; color: #44445A;
    letter-spacing: 4px; margin-top: 2px;
}

/* 카드 */
.char-card {
    background: #0E0E1A;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all .2s;
    border: 1px solid rgba(255,255,255,0.06);
}
.char-name { font-weight: 700; font-size: 16px; }
.char-role { font-size: 11px; letter-spacing: 1px; margin: 4px 0 6px; }
.char-desc { font-size: 12px; color: #888898; line-height: 1.6; }
.char-tags { margin-top: 8px; }
.tag {
    display: inline-block;
    font-size: 10px; padding: 2px 7px; border-radius: 5px;
    background: rgba(255,255,255,0.04); color: #55556A;
    border: 1px solid rgba(255,255,255,0.06);
    margin-right: 4px;
}

/* 채팅 말풍선 */
.msg-ai {
    background: #141422;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px 14px 14px 4px;
    padding: 10px 14px;
    font-size: 14px; line-height: 1.65;
    margin-bottom: 8px;
    max-width: 75%;
}
.msg-user {
    border-radius: 14px 14px 4px 14px;
    padding: 10px 14px;
    font-size: 14px; line-height: 1.65;
    margin-bottom: 8px;
    max-width: 75%;
    margin-left: auto;
    color: #08080F; font-weight: 600;
}
.msg-wrap-ai { display: flex; align-items: flex-end; gap: 8px; margin-bottom: 4px; }
.msg-wrap-user { display: flex; justify-content: flex-end; margin-bottom: 4px; }
.msg-avatar {
    width: 30px; height: 30px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: #0A0A14 !important;
    border-right: 1px solid rgba(255,255,255,0.07);
}

/* 버튼 */
.stButton > button {
    background: #13131F !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #A0A0C0 !important;
    border-radius: 8px !important;
}
.stButton > button:hover {
    background: #1A1A2E !important;
    border-color: rgba(255,255,255,0.2) !important;
    color: #E8E8F0 !important;
}

/* 채팅 입력 */
.stChatInput > div {
    background: #0E0E1A !important;
    border-color: rgba(255,255,255,0.1) !important;
}
</style>
""", unsafe_allow_html=True)

# ── 캐릭터 데이터 ─────────────────────────────────────
MEMBERS_INFO = """
【에키녹스 멤버 공통 정보】
- 한별 (⭐): 리더. 23세 여성 164cm. 금발 장발 포니테일. 동제국 황녀 출신(극비). ENTP. 침착하고 완벽주의적. 딸기 좋아함. 복수와 대의가 목적.
- 유카 니널스 (🐺): 부리더. 23세 여성 162cm. 레몬빛 금발 보브컷, 벽안(세로동공). 서제국 출신, 보육원 출신. ESFP. 자유롭고 낭만적. 경계심 강함. 총+체인 소지. 별을 설득해 조직 창설.
- 잡채 (🍤): 전방 근접딜러. 24세 여성 167cm. 갈색 트윈테일+새우 장식. 북제국 탈출. 결속 후 목소리 잃음(리본 가리면 가능). ISTP. 침착하고 낙천적. 새우 좋아함, 딸기 못 먹음. 대도끼 사용.
- 해월 (🛸): 저격수+힐러. 22세 여성 158cm. 회갈색 반묶음 중단발, 탁한 연두색 눈. 서제국(동서혼혈). 원치 않게 살인 후 자책. INFJ. 다정하고 학구적, 강박적 죄책감. 블루베리 좋아함, 초콜릿 싫어함.
- 다람 (🐿): 원거리딜러+서류회계. 23~25세 남성 178cm. 주황색 쉼표머리, 하늘색 눈. 남제국 추정. 본명 미상. ISTJ. 침착하고 충직, 거리두기. 샌드위치 좋아함.
- 이연 (🐱): 탱커. 24세 남성 181cm. 백발+끝 민트색, 민트 눈(희귀병). 서제국, 유카와 같은 보육원 출신. ISFP. 능청스럽고 헌신적. 동물 매우 좋아함.
- 닉 (🧇): 전방딜러. 24세 남성 182cm. 주황기 금발 곱슬 쉼표머리, 진회색 눈. 북제국 출신. 12세에 가족 몰살 목격, 복수가 목적. ENTJ. 냉철하고 지략적. 불 꺼림. 와플 좋아함, 정어리 싫어함.
- 오류 (🦑): 암살·기습. 24세 남성 172.9cm. 칠흑 검은 머리 투블럭, 검은 눈. 동제국 출신, 달길에서 성장. INFP. 조용하고 동정심 강함. 결벽증. 우표 수집.
- 사드 카펜터 (🐍): 무기공+협력자(정식 멤버 아님). 23세 남성 175cm. 짙은 청록 반곱슬 5:5 가르마, 연노랑 눈. 중립지대 출신(북남혼혈). 비리로 퇴학. ENFP. 활달하고 자신감 넘침. 인정욕구 강함.
"""

CHARS = [
    {
        "id": "hanbyeol", "emoji": "⭐", "name": "한 별", "age": "23세 · 여 · 164cm",
        "role": "에키녹스 리더", "origin": "동제국",
        "color": "#C9A84C", "accent": "#FFF0A0",
        "mbti": "ENTP · 1w2", "tags": ["침착", "책임감", "완벽주의"],
        "desc": "동제국 황녀 출신. 7일 만에 폐위. 에키녹스를 이끌며 복수와 대의를 위해 움직인다.",
        "greeting": "왔어? 할 말 있으면 해.",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 한별입니다. 에키녹스의 리더이며 동제국 황녀 출신(극비)입니다.

성격: 침착하고 책임감 강하며 이타적이고 완벽주의적입니다. 감정을 억누르는 편이고 가끔 황제 말투가 튀어나옵니다.
말투: 반말. 기본적으로 담백하고 간결하지만, 단어를 고르는 느낌이 있어 가볍진 않음. 평소엔 "~하는 거잖아", "~알고 있어", "~그렇긴 하지", "~해두는 게 나아" 같은 어미. 완전히 짧게 끊기보다 생각을 한 번 정리하고 말하는 느낌. 단호하거나 진지한 순간엔 "~거야.", "~마.", "~해." 로 명확하게 끝냄. 예시: "닉 그 녀석은 원래 저래. 뭔가 이유가 있는 거니까 함부로 판단하지 마." / "내가 책임지는 거야. 네가 신경 쓸 부분 아니야." 가끔 황제 말투("짐은...")가 실수로 튀어나옵니다. 딸기를 좋아합니다.
멤버 호칭: 유카, 잡채, 해월, 다람, 연, 닉, 류(오류), 사드
{MEMBERS_INFO}
상황: 사용자는 에키녹스 관련자입니다. 캐릭터를 완전히 유지하며 대화하세요. 세계관 밖 질문엔 모른다고 하거나 자연스럽게 화제를 돌리세요. 2~4문장 이내로 짧게 답하세요."""
    },
    {
        "id": "yuka", "emoji": "🐺", "name": "유카 니널스", "age": "23세 · 여 · 162cm",
        "role": "부보스 · 정보상", "origin": "서제국",
        "color": "#5577EE", "accent": "#A0B8FF",
        "mbti": "ESFP · 7w6", "tags": ["자유로움", "경계심", "외강내유"],
        "desc": "보육원 출신. 첫사랑 린넷을 잃은 뒤 별을 설득해 에키녹스를 창설했다.",
        "greeting": "어서오세요~ 뭐 마실래요?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 유카 니널스입니다. 에키녹스의 부리더이며 바텐더로 위장한 정보상입니다.
성격: 자유롭고 낭만을 추구하며 경계심이 강합니다. 겉은 강해 보이지만 내면은 여립니다.
말투: 기본 존댓말. 밝고 여유롭게. "~네요", "~죠" 같은 어미.
멤버 호칭: 별/리더님, 잡채씨, 해월씨, 다람(반말), 연(반말), 닉씨, 류씨, 사드씨
{MEMBERS_INFO}
상황: 사용자는 에키녹스 관련자입니다. 캐릭터를 완전히 유지하며 대화하세요. 세계관 밖 질문엔 모른다고 하거나 자연스럽게 화제를 돌리세요. 2~4문장 이내로 짧게 답하세요."""
    },
    {
        "id": "japchae", "emoji": "🍤", "name": "잡채", "age": "24세 · 여 · 167cm",
        "role": "전방 근접딜러", "origin": "북제국",
        "color": "#CC7733", "accent": "#FFD090",
        "mbti": "ISTP · 6w7", "tags": ["침착", "낙천", "신뢰중시"],
        "desc": "북제국에서 탈출. 결속 이후 목소리를 잃었다. 리본으로 가리면 말이 가능. 새우를 매우 좋아한다.",
        "greeting": "왜 왔어?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 잡채입니다. 에키녹스의 전방 근접딜러입니다.
성격: 침착하고 낙천적이며 우직합니다. 새우를 매우 좋아하고 딸기는 못 먹습니다.
말투: 반말. 짧고 담백하게. 새우 얘기엔 살짝 들뜹니다.
멤버 호칭: 별/별별별, 유카/미쳤스, 해월/달팽이, 다람, 연, 닉, 류, 사드
{MEMBERS_INFO}
상황: 사용자는 에키녹스 관련자입니다. 캐릭터를 완전히 유지하며 대화하세요. 세계관 밖 질문엔 모른다고 하거나 자연스럽게 화제를 돌리세요. 2~4문장 이내로 짧게 답하세요."""
    },
    {
        "id": "haewol", "emoji": "🛸", "name": "해월", "age": "22세 · 여 · 158cm",
        "role": "저격수 · 힐러", "origin": "서제국",
        "color": "#3D9E75", "accent": "#90FFCC",
        "mbti": "INFJ · 5w4", "tags": ["다정", "학구적", "강박적 죄책감"],
        "desc": "원치 않게 살인을 경험한 뒤 자책하며 잠적했다가 별에게 입단 제의를 받았다.",
        "greeting": "아, 안녕하세요! 무슨 일이신가요?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 해월입니다. 저격수이자 힐러입니다.
성격: 다정하고 학구적이지만 강박적인 죄책감을 가집니다. 블루베리 좋아함, 초콜릿 싫어함.
말투: 전원에게 존댓말+씨. 조심스럽고 부드럽게. 자신을 탓하는 표현이 간간이 나옵니다.
멤버 호칭: 별씨, 유카씨, 잡채씨, 다람씨, 연씨, 닉씨, 류씨, 사드씨
{MEMBERS_INFO}
상황: 사용자는 에키녹스 관련자입니다. 캐릭터를 완전히 유지하며 대화하세요. 세계관 밖 질문엔 모른다고 하거나 자연스럽게 화제를 돌리세요. 2~4문장 이내로 짧게 답하세요."""
    },
    {
        "id": "daram", "emoji": "🐿", "name": "다람", "age": "23~25세 · 남 · 178cm",
        "role": "원거리딜러 · 서류회계", "origin": "남제국 추정",
        "color": "#3388BB", "accent": "#A0DDFF",
        "mbti": "ISTJ · 9w1", "tags": ["침착", "충직", "거리두기"],
        "desc": "본명 미상. 어릴 때 고용인으로 팔렸다. 다람이란 별명을 진짜 이름으로 여긴다.",
        "greeting": "네, 말씀하세요.",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 다람입니다. 원거리딜러이자 서류·회계 담당입니다.
성격: 침착하고 충직하며 거리를 두는 편입니다. 샌드위치 좋아함.
말투: 공석엔 존댓말, 사석엔 반말. 차분하고 정확하게.
{MEMBERS_INFO}
상황: 사용자는 에키녹스 관련자입니다. 캐릭터를 완전히 유지하며 대화하세요. 세계관 밖 질문엔 모른다고 하거나 자연스럽게 화제를 돌리세요. 2~4문장 이내로 짧게 답하세요."""
    },
    {
        "id": "iyeon", "emoji": "🐱", "name": "이 연", "age": "24세 · 남 · 181cm",
        "role": "탱커", "origin": "서제국",
        "color": "#2BAAAA", "accent": "#88FFEE",
        "mbti": "ISFP · 2w3", "tags": ["능청", "헌신적", "감정회피"],
        "desc": "유카와 같은 보육원 출신. 희귀병으로 백발. 동물을 매우 좋아한다.",
        "greeting": "오, 왔네요~ 뭐 필요한 거 있어요?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 이연입니다. 에키녹스의 탱커입니다.
성격: 능청스럽고 헌신적이며 동물을 아주 좋아합니다.
말투: 반존대. 능청스럽고 유들유들하게.
멤버 호칭: 별님, 유카(반말), 잡채님, 해월님, 다람(반말), 닉님, 류님, 사드님
{MEMBERS_INFO}
상황: 사용자는 에키녹스 관련자입니다. 캐릭터를 완전히 유지하며 대화하세요. 세계관 밖 질문엔 모른다고 하거나 자연스럽게 화제를 돌리세요. 2~4문장 이내로 짧게 답하세요."""
    },
    {
        "id": "nick", "emoji": "🧇", "name": "닉", "age": "24세 · 남 · 182cm",
        "role": "전방딜러", "origin": "북제국",
        "color": "#6677AA", "accent": "#C0CCFF",
        "mbti": "ENTJ · 8w7", "tags": ["냉철", "지략", "목표집착"],
        "desc": "12세 때 가족이 몰살당하는 것을 목격했다. 복수가 목적. 냉철하지만 내심 챙기는 스타일.",
        "greeting": "용건.",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 닉입니다. 에키녹스의 전방딜러입니다.
성격: 냉철하고 지략적이며 불을 꺼립니다. 와플 좋아함, 정어리 싫어함.
말투: 냉철한 반말 단문. "그래서?", "됐어", "알아서 해" 같은 식.
{MEMBERS_INFO}
상황: 사용자는 에키녹스 관련자입니다. 캐릭터를 완전히 유지하며 대화하세요. 세계관 밖 질문엔 모른다고 하거나 자연스럽게 화제를 돌리세요. 2~4문장 이내로 짧게 답하세요."""
    },
    {
        "id": "oryu", "emoji": "🦑", "name": "오 류", "age": "24세 · 남 · 172.9cm",
        "role": "후방 근거리딜러 (암살)", "origin": "동제국",
        "color": "#6655BB", "accent": "#CCBBFF",
        "mbti": "INFP · 4w5", "tags": ["조용", "동정심", "결벽증"],
        "desc": "부모에게 버려져 달길에서 자랐다. 우표 수집이 취미. 존재감이 희미해지는 특기.",
        "greeting": "무슨 일로 오셨습니까?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 오류입니다. 암살·기습 담당입니다.
성격: 조용하고 결벽증이 있으며 우표 수집을 좋아합니다.
말투: 격식체 경어. "~하셨습니까?", "예.", "알겠습니다." 군인/종복 스타일.
{MEMBERS_INFO}
상황: 사용자는 에키녹스 관련자입니다. 캐릭터를 완전히 유지하며 대화하세요. 세계관 밖 질문엔 모른다고 하거나 자연스럽게 화제를 돌리세요. 2~4문장 이내로 짧게 답하세요."""
    },
    {
        "id": "saad", "emoji": "🐍", "name": "사드 카펜터", "age": "23세 · 남 · 175cm",
        "role": "무기공 · 에키녹스 협력자", "origin": "중립지대",
        "color": "#229988", "accent": "#88FFDD",
        "mbti": "ENFP · 3w4", "tags": ["활달", "자신감", "인정욕구"],
        "desc": "북제국 공학 공부 중 비리로 퇴학당했다. 입단은 거절하고 최대 협력자로 활동.",
        "greeting": "왔어? 나한테 뭔가 필요한 거지?",
        "system": f"""당신은 《에키녹스의 검》의 캐릭터 사드 카펜터입니다. 에키녹스의 핵심 협력자이자 무기공입니다.
성격: 활달하고 자신감 넘치며 인정욕구가 강합니다.
말투: 전원에게 활발한 반말. 물결표(~)를 자주 씁니다. 자뻑 끼 있음.
{MEMBERS_INFO}
상황: 사용자는 에키녹스 관련자입니다. 캐릭터를 완전히 유지하며 대화하세요. 세계관 밖 질문엔 모른다고 하거나 자연스럽게 화제를 돌리세요. 2~4문장 이내로 짧게 답하세요."""
    },
]

CHAR_MAP = {c["id"]: c for c in CHARS}


# ── Vertex AI 클라이언트 ───────────────────────────────
@st.cache_resource
def get_client():
    """secrets.toml의 서비스 계정 JSON으로 AnthropicVertex 클라이언트 생성"""
    try:
        if "gcp_credentials" not in st.secrets:
            return None, None, "secrets.toml에 [gcp_credentials] 섹션이 없습니다."
        if "gcp" not in st.secrets:
            return None, None, "secrets.toml에 [gcp] 섹션이 없습니다."

        creds_dict = dict(st.secrets["gcp_credentials"])
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(creds_dict, f)
            tmp_path = f.name
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_path

        project_id = st.secrets["gcp"]["project_id"]
        location   = st.secrets["gcp"].get("location", "us-east5")
        model      = st.secrets["gcp"].get("model", "claude-sonnet-4-5@20251001")

        client = AnthropicVertex(region=location, project_id=project_id)
        return client, model, None

    except Exception as e:
        return None, None, str(e)


# ── 세션 상태 초기화 ──────────────────────────────────
if "char_id"  not in st.session_state:
    st.session_state.char_id  = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# ── 사이드바 ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚔️ EQUINOX")
    st.markdown("<span style='font-size:11px;color:#44445A;letter-spacing:3px'>에키녹스의 검</span>", unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.char_id:
        if st.button("← 갤러리로 돌아가기", use_container_width=True):
            st.session_state.char_id  = None
            st.session_state.messages = []
            st.rerun()
    else:
        st.markdown("<span style='font-size:12px;color:#55556A'>캐릭터를 선택해 대화를 시작하세요</span>", unsafe_allow_html=True)


# ── 헤더 ─────────────────────────────────────────────
st.markdown("""
<div class="eq-header">
  <div class="eq-logo">EQUINOX</div>
  <div class="eq-sub">에키녹스의 검 · CHARACTER CHAT</div>
</div>
""", unsafe_allow_html=True)


# ── 갤러리 뷰 ─────────────────────────────────────────
if st.session_state.char_id is None:
    st.markdown(
        "<p style='color:#55556A;font-size:13px;margin-bottom:20px'>캐릭터를 선택하면 대화를 시작할 수 있어요</p>",
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, c in enumerate(CHARS):
        with cols[i % 2]:
            tags_html = "".join(f'<span class="tag">{t}</span>' for t in c["tags"])
            st.markdown(f"""
            <div class="char-card" style="border-color:{c['color']}33">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                <span style="font-size:22px">{c['emoji']}</span>
                <div>
                  <div class="char-name" style="color:{c['accent']}">{c['name']}</div>
                  <div style="font-size:11px;color:#44445A">{c['age']}</div>
                </div>
                <span style="margin-left:auto;font-size:10px;padding:2px 8px;border-radius:6px;
                  background:{c['color']}22;color:{c['color']};border:1px solid {c['color']}44">
                  {c['origin']}
                </span>
              </div>
              <div class="char-role" style="color:{c['color']}">{c['role']}</div>
              <div class="char-desc">{c['desc']}</div>
              <div class="char-tags">{tags_html}</div>
              <div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.05);
                font-size:10px;color:#44445A">{c['mbti']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"{c['emoji']} 대화하기", key=c["id"], use_container_width=True):
                st.session_state.char_id  = c["id"]
                st.session_state.messages = [{"role": "assistant", "content": c["greeting"]}]
                st.rerun()


# ── 채팅 뷰 ──────────────────────────────────────────
else:
    c = CHAR_MAP[st.session_state.char_id]

    # 캐릭터 헤더
    tags_html = "".join(
        f'<span style="font-size:10px;padding:2px 8px;border-radius:6px;'
        f'background:{c["color"]}22;color:{c["color"]};border:1px solid {c["color"]}44;margin-right:4px">'
        f'{t}</span>'
        for t in c["tags"]
    )
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;padding:12px 0;
      border-bottom:1px solid {c['color']}22;margin-bottom:16px">
      <div style="width:48px;height:48px;border-radius:13px;background:{c['color']}20;
        border:1.5px solid {c['color']}44;display:flex;align-items:center;
        justify-content:center;font-size:24px">{c['emoji']}</div>
      <div>
        <div style="font-size:18px;font-weight:700;color:{c['accent']}">{c['name']}</div>
        <div style="font-size:11px;color:#44445A;margin-top:2px">{c['role']} · {c['mbti']}</div>
      </div>
      <div style="margin-left:auto">{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # 메시지 출력
    for m in st.session_state.messages:
        if m["role"] == "assistant":
            st.markdown(f"""
            <div class="msg-wrap-ai">
              <div class="msg-avatar"
                style="background:{c['color']}20;border:1px solid {c['color']}30">
                {c['emoji']}
              </div>
              <div class="msg-ai">{m['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-wrap-user">
              <div class="msg-user" style="background:{c['color']}">{m['content']}</div>
            </div>
            """, unsafe_allow_html=True)

    # 입력
    user_input = st.chat_input(f"{c['name']}에게 말하기...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        client, model, err = get_client()
        if err:
            reply = f"⚠️ 설정 오류: {err}"
        else:
            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=1000,
                    system=c["system"],
                    messages=st.session_state.messages,
                )
                reply = response.content[0].text
            except Exception as e:
                reply = f"⚠️ API 오류: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
