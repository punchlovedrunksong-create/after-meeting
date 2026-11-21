# MVP 웹 서비스 구조 설계

작성: Planner / 2026-11-15

## 1. 설계 기준

- 기준 문서: `requirements.md`, `function-breakdown.md`, `mvp-plan.md`
- 대상: 분석 이력과 데이터베이스가 없는 단일 TXT 회의 분석 MVP
- 기술 구성: FastAPI Backend, React + Vite Frontend, OpenAI Chat Completions API (`gpt-6-luna`, `reasoning_effort=high`)
- 키트 적용: 프로젝트 구조 설계 기준만 반영했다. `vibe-frame-kit`의 원본 파일은 앱에 복사하지 않는다.
- API 키: 미정. 각 개발자가 발급받아 Backend 서버의 로컬 `.env`에만 설정한다.

## 2. 사용자 흐름 및 데이터 흐름

```text
사용자가 TXT 선택·제출
  → Frontend가 확장자·10MB 초과 여부를 빠르게 안내
  → POST /api/v1/analyses (multipart/form-data: file)
  → API가 DocumentService에 파일 검증·읽기 위임
  → AnalysisWorkflow가 원문을 요약하고 요약 결과를 검증
  → 검증된 요약으로 투두 생성 후 항목 검증
  → API가 summary + todos만 응답
  → Frontend가 결과 두 영역을 표시
```

파일 및 AI 오류는 표준 오류 응답으로 종료한다. 각 AI 단계는 최대 1회 재시도한다. 영속 저장·분석 ID·이력 API는 두지 않는다. 원문은 설정한 외부 AI 서비스로 전송되므로 실제 제공자 선택 전 데이터 취급 조건을 확인한다.

## 3. Frontend와 Backend 역할

| 영역 | 책임 | 구현 위치 |
| --- | --- | --- |
| Frontend | 파일 선택, 빠른 클라이언트 검증, 요청 중/오류/성공 상태, 요약·투두 표시 | `frontend/src/App.jsx`, `components/`, `services/api.js` |
| Backend API | multipart 요청 수신, 서비스 호출, 성공·오류 응답 경계 | `backend/app/api/routes/`, `api/schemas/`, `main.py` |
| 문서 처리 | 서버에서 파일 형식·크기·디코딩·빈 내용 검증 | `backend/app/services/document_service.py` |
| 분석 흐름 | 요약 → 형식 검증 → 투두 → 형식 검증, 제한 재시도 | `backend/app/agents/workflow.py` |
| AI 연결 | 환경 설정 확인, OpenAI Chat Completions 호출, high 추론 강도, JSON 파싱, 민감 내용 없이 오류 분류 | `backend/app/services/ai_service.py` |

## 4. 계층 책임과 주요 입출력

| 모듈 | 입력 | 처리 | 출력 |
| --- | --- | --- | --- |
| API (`routes/analyses.py`) | `UploadFile`의 `file` | DocumentService와 AnalysisWorkflow를 순서대로 호출하고 파일을 닫음 | `AnalysisResult` 또는 안전한 오류 |
| Document Service | 업로드 파일 | `.txt`, 최대 10MB, 지원 인코딩, 빈 내용 검사 | 공백을 정리한 `meeting_text: str` |
| AI Workflow | `meeting_text: str` | 프롬프트 구성, 요약과 투두 순차 호출, 스키마·줄 수 검사, 최대 1회 재시도 | `AnalysisResult(summary, todos)` |
| AI Service | 시스템/사용자 프롬프트 | 서버 환경 변수 기반 Chat Completions 호출 및 JSON 파싱 | 파싱된 AI 데이터 객체 |
| Model | 파싱된 dict/list | `MeetingSummary`, `TodoItem`, `AnalysisResult` 계약 검증 | 타입이 정해진 내부/응답 모델 |
| Core | 설정 및 예외 | 환경 설정, 공통 오류 코드·상태·사용자 조치 관리 | 설정 객체 및 API 오류 응답 |
| Frontend API Client | `File` | FormData 전송, 성공/오류 JSON 변환 | 분석 결과 객체 또는 사용자 표시용 오류 |

## 5. 최소 API

| Method | 경로 | 입력 | 출력 | 역할 |
| --- | --- | --- | --- | --- |
| `GET` | `/api/health` | 없음 | `{"status":"ok"}` | Backend 프로세스 상태 확인 |
| `POST` | `/api/v1/analyses` | multipart `file` (TXT, 최대 10MB) | `summary` 4개 필드와 `todos[]` | 한 번의 업로드를 동기 분석하고 결과 반환 |

오류는 `{ "error": { "code", "message", "action" } }` 형식으로 전달한다. 세부 입력과 상태 코드는 `api-spec.md`를 기준으로 한다. 분석 ID, 조회·삭제·이력 API는 MVP에 없다.

## 6. 권장 및 현재 디렉터리 구조

```text
after-meeting/
├── README.md
├── .env.example
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── api/
│       │   ├── routes/       # HTTP 경로와 서비스 호출
│       │   └── schemas/      # API 응답 계약
│       ├── agents/           # 고정 순차 분석 workflow
│       ├── core/             # 환경 설정과 공통 오류
│       ├── models/           # 요약·투두 데이터 모델
│       └── services/         # 문서 처리와 외부 AI 연결
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── components/       # 파일 입력·상태·결과 UI
│       ├── services/         # Backend API client
│       └── styles.css
└── docs/
    ├── requirements.md
    ├── function-breakdown.md
    ├── mvp-plan.md
    ├── project-structure.md
    ├── api-spec.md
    ├── agent-workflow.md
    └── test-scenarios.md
```

현재 구현도 위 구조를 사용한다. 라우터, 입력 처리, AI 연결, 워크플로, 모델, 화면을 분리해 이후 제공자 결정이나 UI 수정이 다른 계층에 번지지 않도록 한다.

## 7. MVP 기능과 위치

| 기능 | 주요 위치 |
| --- | --- |
| TXT 업로드, 파일 형식/크기 사전 안내 | `frontend/src/components/FileUpload.jsx` |
| 서버 형식·크기·인코딩·빈 내용 검사 | `backend/app/services/document_service.py` |
| 업로드 분석 API | `backend/app/api/routes/analyses.py` |
| 요약, 형식 검사, 투두 생성, 재시도 | `backend/app/agents/workflow.py` |
| AI 제공자 호출과 JSON 파싱 | `backend/app/services/ai_service.py` |
| 요약·투두 스키마 | `backend/app/models/analysis.py` |
| 오류 매핑·CORS·앱 구성 | `backend/app/core/`, `backend/app/main.py` |
| 요청 중·오류·성공 UI | `frontend/src/App.jsx`, `components/StatusMessage.jsx` |
| 요약·투두 결과 UI | `frontend/src/components/SummaryResult.jsx`, `TodoList.jsx` |
| API 계약·작업 흐름·실행 안내 | `docs/api-spec.md`, `docs/agent-workflow.md`, `README.md` |

## 8. MVP에서 만들지 않는 구조

- 데이터베이스, 저장소 추상화, 분석 이력, 사용자 계정 및 인증
- 업로드 파일 영구 저장, 다운로드, PDF 생성
- 음성 입력, STT, 직접 텍스트 입력
- 큐/백그라운드 작업, 진행률 polling, 복잡한 상태 저장소
- 범용 에이전트 프레임워크, 그래프 오케스트레이션, 도구 호출, RAG/벡터 DB
- 배포 자동화와 운영용 모니터링 체계

현재 흐름은 두 단계의 고정 AI 처리로 충분하며, 별도 저장·검색·비동기 작업 요구가 생길 때 해당 구조를 다시 설계한다.

## 9. 추가 결정 및 통과 기준

| 항목 | 결정 주체 / 확인 방법 | 영향 |
| --- | --- | --- |
| OpenAI API 키 발급·결제 | 각 개발자/프로젝트 소유자, API 플랫폼에서 발급하고 로컬 설정 | 실제 요청 실행과 API 비용 |
| 원문 외부 전송·보관 조건 | 팀/강사, 공급자 데이터 정책 및 사용자 고지 확인 | 개인정보 안내와 실제 서비스 사용 가능성 |
| 투두 우선순위 허용 값 | 팀, 고정 회의 TXT로 표현을 합의 | 응답 정규화와 UI 표시 |
| R-03 필드 필수 여부와 미확인 값 생략 규칙 | 팀/강사, 요구사항과 최신 기능 분해표를 대조 | Model의 nullable/required 계약 |
| AI 품질 수용 기준 및 고정 샘플 | 팀 검토자, 요약·투두를 원문과 대조 | MVP 품질 완료 판정 |

- 설계 판정: **통과** — 사용자 경로, 최소 API, 모듈 책임, MVP 포함/제외 범위와 추적 문서를 정리했다.
- 구현 판정: **확인 필요** — 웹 흐름과 Backend 연결 코드는 있으나, 이 변경에서 런타임·브라우저·외부 AI 시연 검증을 실행하지 않았다.
- 남은 검증: macOS에서 README 절차로 실행, 파일 오류 시나리오와 성공 화면 확인, API 키 설정 후 고정 샘플 품질 확인.
