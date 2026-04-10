import json
import tempfile
import os
import streamlit as st

st.set_page_config(page_title="디버그", page_icon="🔧")

st.title("🔧 Vertex AI 디버그")

# 1. secrets 확인
if "gcp_service_account" in st.secrets:
    creds_dict = dict(st.secrets["gcp_service_account"])
    st.success(f"✅ project_id: {creds_dict.get('project_id', '없음')}")
    st.success(f"✅ client_email: {creds_dict.get('client_email', '없음')}")
else:
    st.error("❌ gcp_service_account 섹션 없음")
    st.stop()

# 2. gcp 섹션 확인
if "gcp" in st.secrets:
    gcp = dict(st.secrets["gcp"])
    st.warning(f"⚠️ [gcp] 섹션 발견: {gcp}")
else:
    st.info("ℹ️ [gcp] 섹션 없음 (기본값 사용)")

# 3. 인증 설정
with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
    json.dump(creds_dict, f)
    tmp_path = f.name
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_path

# 4. Vertex AI 초기화
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel

    project_id = creds_dict["project_id"]
    location = "us-central1"
    vertexai.init(project=project_id, location=location)
    st.success(f"✅ Vertex AI 초기화 성공 (location: {location})")
except Exception as e:
    st.error(f"❌ Vertex AI 초기화 실패: {e}")
    st.stop()

# 5. 모델 테스트
test_models = [
    "gemini-2.5-pro-preview-06-05",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.0-flash",
    "gemini-1.5-pro-002",
    "gemini-1.5-flash-002",
]

st.subheader("모델 테스트")
for model_name in test_models:
    try:
        model = GenerativeModel(model_name)
        response = model.generate_content("안녕이라고만 답해")
        st.success(f"✅ {model_name}: {response.text[:50]}")
    except Exception as e:
        st.error(f"❌ {model_name}: {e}")
