import json
import tempfile
import os
import streamlit as st

st.set_page_config(page_title="디버그", page_icon="🔧")
st.title("🔧 Vertex AI 디버그 v3")

st.cache_resource.clear()
st.cache_data.clear()

if "gcp_service_account" not in st.secrets:
    st.error("❌ gcp_service_account 없음")
    st.stop()

creds_dict = dict(st.secrets["gcp_service_account"])
st.success(f"✅ project_id: {creds_dict.get('project_id')}")

# ── 서비스 계정 키로 직접 인증 (scope 명시) ──
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

try:
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES
    )
    st.success("✅ 서비스 계정 인증 성공")
except Exception as e:
    st.error(f"❌ 인증 실패: {e}")
    st.stop()

# ── Vertex AI 초기화 (credentials 직접 전달) ──
import vertexai
from vertexai.generative_models import GenerativeModel

project_id = creds_dict["project_id"]
location = "us-central1"

try:
    vertexai.init(
        project=project_id,
        location=location,
        credentials=credentials,
    )
    st.success(f"✅ Vertex AI 초기화 성공 ({location})")
except Exception as e:
    st.error(f"❌ 초기화 실패: {e}")
    st.stop()

# ── 모델 테스트 ──
st.subheader("모델 테스트")

test_models = [
    "gemini-2.0-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-pro-002",
    "gemini-2.5-pro-preview-06-05",
    "gemini-2.5-flash-preview-05-20",
]

for model_name in test_models:
    try:
        model = GenerativeModel(model_name)
        response = model.generate_content("안녕이라고만 답해")
        st.success(f"✅ {model_name}: {response.text[:80]}")
    except Exception as e:
        st.error(f"❌ {model_name}: {str(e)[:120]}")
