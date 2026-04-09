# Equinox[README.md](https://github.com/user-attachments/files/26608114/README.md)
# ⚔️ EQUINOX 에키녹스의 검 — 캐릭터 채팅

에키녹스 멤버 9명과 대화할 수 있는 Streamlit 웹앱입니다.
Google Cloud Vertex AI (Claude) 로 구동돼요.

---

## 배포 순서

### 1. Google Cloud 설정

1. [console.cloud.google.com](https://console.cloud.google.com) 접속
2. **Vertex AI API** 검색 → **사용 설정**
3. **IAM 및 관리자 → 서비스 계정** → **만들기**
   - 역할: `Vertex AI 사용자` 선택
4. 만든 서비스 계정 클릭 → **키 탭** → **키 추가 → JSON**
   - JSON 파일 다운로드

### 2. GitHub에 올리기

```
equinox-chat/
├── app.py
├── requirements.txt
├── secrets.toml.example   ← 참고용 (절대 실제 키 올리지 말 것)
└── .gitignore             ← secrets.toml 자동 제외됨
```

```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/유저명/레포이름.git
git push -u origin main
```

### 3. Streamlit Cloud 배포

1. [share.streamlit.io](https://share.streamlit.io) 접속 → GitHub 연결
2. 레포 선택 → `app.py` 선택 → **Deploy**
3. 배포 후 **Settings → Secrets** 탭에 아래 내용 붙여넣기:

```toml
[gcp]
project_id = "내-프로젝트-id"
location   = "us-east5"
model      = "claude-sonnet-4-5@20251001"

[gcp_credentials]
type            = "service_account"
project_id      = "내-프로젝트-id"
private_key_id  = "..."
private_key     = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email    = "...@....iam.gserviceaccount.com"
client_id       = "..."
auth_uri        = "https://accounts.google.com/o/oauth2/auth"
token_uri       = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url        = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

> JSON 파일을 열면 위 항목들이 그대로 다 들어있어요. 복사해서 붙여넣으면 돼요.

### 4. 완료!

Streamlit Cloud가 자동으로 `requirements.txt`를 설치하고 앱을 실행해요.
