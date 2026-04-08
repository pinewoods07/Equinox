# Anthropic API 키를 여기에 입력하세요
# https://console.anthropic.com 에서 발급
VITE_ANTHROPIC_API_KEY=sk-ant-여기에_키_입력

node_modules
dist
.env
.env.local

<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>EQUINOX — 에키녹스의 검</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap" rel="stylesheet" />
    <style>
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { background: #0A0A0F; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>

{
  "name": "equinox-chat",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.2"
  }
}

# ⚔️ EQUINOX — 에키녹스의 검 캐릭터 채팅

에키녹스의 검 세계관 캐릭터 9명과 직접 대화할 수 있는 인터랙티브 채팅 앱입니다.

## 캐릭터

| 이름 | 역할 |
|------|------|
| ⭐ 한 별 | 에키녹스 리더 |
| 🐺 유카 니널스 | 부리더 · 정보상 |
| 🍤 잡채 | 전방 근접딜러 |
| 🛸 해월 | 저격수 · 힐러 |
| 🐿 다람 | 원거리딜러 · 서류회계 |
| 🐱 이 연 | 탱커 |
| 🧇 닉 | 전방딜러 |
| 🦑 오 류 | 암살 · 기습 |
| 🐍 사드 카펜터 | 무기공 · 협력자 |

## 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열고 Anthropic API 키를 입력하세요:

```
VITE_ANTHROPIC_API_KEY=sk-ant-여기에_키_입력
```

> API 키는 [Anthropic Console](https://console.anthropic.com) 에서 발급받을 수 있어요.

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 `http://localhost:5173` 으로 접속하면 돼요.

### 4. 빌드 (배포용)

```bash
npm run build
```

## 기술 스택

- React 18 + Vite
- Anthropic Claude API (`claude-sonnet-4-20250514`)

## 주의사항

- API 키는 절대 깃허브에 올리지 마세요. `.gitignore`에 `.env`가 포함되어 있어요.
- Vite 개발 서버의 프록시(`/api/anthropic`)를 통해 API 키가 브라우저에 노출되지 않도록 설정되어 있어요.
- 프로덕션 배포 시에는 별도의 백엔드 서버(Express, Next.js 등)를 사용하는 것을 권장해요.

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api/anthropic": {
        target: "https://api.anthropic.com",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/anthropic/, ""),
        headers: {
          "x-api-key": process.env.VITE_ANTHROPIC_API_KEY || "",
          "anthropic-version": "2023-06-01",
        },
      },
    },
  },
});
