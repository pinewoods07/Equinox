import json
import tempfile
import os
import streamlit as st

st.set_page_config(page_title="디버그", page_icon="🔧")
st.title("🔧 Vertex AI 디버그 v2")

# 캐시 전부 클리어
st.cache_resource.clear()
st.cache_data.clear()

# 1. secrets 확인
if "gcp_service_account" in st.secrets:
    creds_dict = dict(st.secrets["gcp_service_account"])
    st.success(f"✅ project_id: {creds_dict.get('project_id', '없음')}")
    st.success(f"✅ client_email: {creds_dict.get('client_email', '없음')}")
else:
    st.error("❌ gcp_service_account 섹션 없음")
    st.stop()

# 2. 인증 설정
with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
    json.dump(creds_dict, f)
    tmp_path = f.name
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_path

# 3. API 활성화 상태 확인
st.subheader("API 활성화 확인")
try:
    from google.auth import default
    from google.auth.transport.requests import Request
    import requests as req

    credentials, project = default()
    credentials.refresh(Request())
    token = credentials.token

    # Vertex AI API 상태 확인
    url = f"https://serviceusage.googleapis.com/v1/projects/{creds_dict['project_id']}/services/aiplatform.googleapis.com"
    headers = {"Authorization": f"Bearer {token}"}
    resp = req.get(url, headers=headers)
    data = resp.json()
    state = data.get("state", "UNKNOWN")
    if state == "ENABLED":
        st.success(f"✅ Vertex AI API: {state}")
    else:
        st.error(f"❌ Vertex AI API: {state}")
        st.info("👉 https://console.cloud.google.com/apis/enableflow?apiid=aiplatform.googleapis.com&project=equinox-492807")
except Exception as e:
    st.warning(f"⚠️ API 상태 확인 실패: {e}")

# 4. Vertex AI 초기화 - 여러 리전 테스트
st.subheader("리전별 모델 테스트")

import vertexai
from vertexai.generative_models import GenerativeModel

test_configs = [
    ("us-central1", "gemini-2.0-flash-001"),
    ("us-central1", "gemini-1.5-flash-001"),
    ("us-central1", "gemini-pro"),
    ("us-east4", "gemini-2.0-flash-001"),
    ("europe-west1", "gemini-2.0-flash-001"),
]

for location, model_name in test_configs:
    try:
        vertexai.init(
            project=creds_dict["project_id"],
            location=location,
            credentials=credentials,
        )
        model = GenerativeModel(model_name)
        response = model.generate_content("say hi")
        st.success(f"✅ {location} / {model_name}: {response.text[:80]}")
    except Exception as e:
        error_msg = str(e)[:150]
        st.error(f"❌ {location} / {model_name}: {error_msg}")

# 5. REST API로 직접 테스트
st.subheader("REST API 직접 테스트")
try:
    project_id = creds_dict["project_id"]
    loc = "us-central1"
    model_id = "gemini-2.0-flash-001"

    url = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{loc}/publishers/google/models/{model_id}:generateContent"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "contents": [{"role": "user", "parts": [{"text": "say hello"}]}]
    }
    resp = req.post(url, headers=headers, json=body)
    st.write(f"HTTP 상태: {resp.status_code}")
    st.json(resp.json())
except Exception as e:
    st.error(f"❌ REST 테스트 실패: {e}")
