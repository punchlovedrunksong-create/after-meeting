# after meeting

이미 STT로 변환된 회의 TXT를 업로드하면 회의 안건·문제점·해결방안·결론을 요약하고, 요약에서 확인되는 후속 업무를 투두리스트로 정리하는 MVP 웹 서비스입니다. 음성 녹음과 STT 변환은 제공하지 않습니다.

## 포함 기능

- TXT 업로드 및 파일 형식·크기(최대 10MB)·빈 내용·문자 인코딩 검사
- AI 기반 회의 요약(회의 안건, 문제점, 해결방안, 결론; 항목별 최대 3줄)
- 검증된 요약을 바탕으로 한 투두리스트 생성
- 근거가 확인되는 경우에만 담당자·기한·우선순위 표시
- 요약과 투두 분리 출력 및 입력/AI 오류 안내
- 일시적인 AI 오류 또는 결과 형식 오류는 최대 1회 재시도

분석 이력·데이터베이스 저장·로그인·직접 텍스트 입력·음성 녹음/STT·다운로드·명함 추출·후속 메일 초안은 MVP 범위에 포함하지 않습니다. 입력 원문은 서버에 저장하지 않지만, 분석을 위해 설정한 외부 AI API로 전송됩니다.

## 기술 구성

- Backend: Python 3.10+, FastAPI, Pydantic, HTTPX
- Frontend: React, Vite, JavaScript
- AI 연결: OpenAI Chat Completions API, `gpt-6-luna`, 추론 강도 `high`.
- 저장소: 없음

## 실행 준비

### 1. AI 설정

프로젝트 루트의 macOS 터미널에서 예시 파일을 복사합니다.

```zsh
cp .env.example .env
```

`.env`에서 OpenAI API 프로젝트 키를 설정합니다. ChatGPT 앱 구독과 API 사용료는 별도이며, 유료 API 사용 전 API 플랫폼의 결제 설정을 확인해야 합니다. API 키는 [OpenAI API 플랫폼](https://platform.openai.com/)에서 발급하고, 키 생성·사용 정보는 [API 키 안내](https://developers.openai.com/api/docs/guides/api-keys)를 참고하세요. 이 서비스는 OpenAI의 `/v1/chat/completions`를 호출하므로 `AI_BASE_URL`에는 `/chat/completions`를 넣지 않습니다.

```env
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-6-luna
AI_REASONING_EFFORT=high
AI_API_KEY=your_secret_key
```

`AI_API_KEY`에는 발급받은 프로젝트 API 키를 입력합니다. 서버는 키 설정 없이 실행할 수 있지만, 분석 요청은 `503` 오류로 종료됩니다. 실제 키를 코드·프런트엔드 환경 변수에 넣거나 저장소에 커밋하지 마세요. API 키는 이 채팅에 붙여 넣지 마세요.

### 2. Backend 실행

프로젝트 루트에서:

```zsh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

가상환경을 직접 지정해 실행하므로 활성화 명령은 필요하지 않습니다.

- 상태 확인: <http://127.0.0.1:8000/api/health>
- API 문서: <http://127.0.0.1:8000/docs>

### 3. Frontend 실행

Backend는 실행한 채로 새 터미널에서:

```zsh
cd frontend
npm install
npm run dev
```

브라우저에서 <http://127.0.0.1:5173>을 엽니다. Backend는 `http://127.0.0.1:5173`과 `http://localhost:5173` 두 개발 Origin을 허용합니다. `.env`의 `FRONTEND_ORIGIN`을 바꿨다면 Backend를 재시작해야 반영됩니다. 기본 API 주소는 `http://127.0.0.1:8000/api`이며 변경하려면 `frontend/.env`에 `VITE_API_BASE_URL`을 설정하세요. Vite 8 사용을 위해 Node.js 20.19+ 또는 22.12+가 필요합니다.

## 사용 방법

1. 이미 STT로 추출된 회의 내용이 들어 있는 `.txt` 파일을 선택합니다.
2. `요약 및 투두 생성`을 눌러 분석을 요청합니다.
3. 회의 요약과 투두리스트를 각각 확인하고 원문과 대조합니다.

지원 문자 인코딩: UTF-8, UTF-8 BOM, UTF-16, CP949. TXT 외 파일 형식은 지원하지 않습니다.

## API 요약

| Method | Endpoint | 설명 |
| --- | --- | --- |
| `GET` | `/api/health` | 서버 상태 확인 |
| `POST` | `/api/v1/analyses` | `multipart/form-data`의 `file` 필드로 TXT를 받고 요약·투두 응답 반환 |

분석 응답은 `summary`(4개 요약 항목)와 `todos` 배열로 구성됩니다. 입력 오류는 `error.code`, `error.message`, `error.action` 구조로 반환됩니다. 업로드 원문과 AI 요청 본문은 브라우저 응답이나 서버 로그에 포함하지 않습니다. 세부 계약은 [API 명세](docs/api-spec.md)를 참고하세요.

AI 호출 오류가 발생하면 Backend 터미널에 원인 분류, 외부 HTTP 상태 코드와 인증정보를 제거한 endpoint 식별 정보가 기록됩니다. API 키, 요청 본문, 제공자 응답 원문은 기록하지 않습니다.

## 주요 파일

```text
backend/app/api/routes/       HTTP API
backend/app/api/schemas/      응답 데이터 형식
backend/app/agents/           요약 → 검증 → 투두 처리 흐름
backend/app/services/         TXT 검증·읽기, AI API 연결
backend/app/models/           요약 및 투두 데이터 모델
frontend/src/components/      업로드·상태·결과 화면
frontend/src/services/api.js  Backend 요청
docs/api-spec.md              API 계약
docs/agent-workflow.md        AI 처리 흐름
docs/project-structure.md     계층 책임과 MVP 구현 위치
docs/test-scenarios.md        확인 시나리오와 실행 상태
```

## 현재 확인 상태

압축 파일에 포함된 기존 기록에는 Windows 환경에서 Backend 의존성 설치, health endpoint, 두 개발 Origin의 CORS 사전 요청을 확인한 것으로 기재되어 있습니다. 이번 변경에서는 해당 검증을 다시 실행하지 않았으며, AI 분석 API와 AI 결과 품질도 검증하지 않았습니다. 과거 실행 증거와 현재 미실행 항목은 [테스트 시나리오](docs/test-scenarios.md)에 구분해 기록했습니다.
