# 분석 API 명세

작성: Builder / 2026-11-15

## 1. 기준과 범위

입력: `docs/requirements.md`, `docs/function-breakdown.md`, `docs/mvp-plan.md`  
범위: 이력·DB 저장이 없는 TXT 업로드 기반 동기 분석 MVP.

## 2. 분석 요청

| 항목 | 내용 |
| --- | --- |
| API 이름 | TXT 회의 분석 |
| Method | `POST` |
| Endpoint | `/api/v1/analyses` |
| 요청 형식 | `multipart/form-data` |
| 필드 | `file`: 필수 TXT 파일, 최대 10MB |
| 처리 | TXT 형식·크기·읽기·빈 내용 확인 후 요약 생성, 요약 검증, 투두 생성 및 검증 |
| 성공 | `200 OK` |

### 성공 응답

```json
{
  "summary": {
    "meeting_agenda": "회의 안건",
    "issues": "논의된 문제점",
    "solutions": "해결방안",
    "conclusion": "결론"
  },
  "todos": [
    {
      "task": "후속 할 일",
      "assignee": "담당자 (근거가 있는 경우에만 포함)",
      "due_date": "기한 (근거가 있는 경우에만 포함)",
      "priority": "우선순위 (근거가 있는 경우에만 포함)"
    }
  ]
}
```

`todos`는 할 일이 없으면 빈 배열입니다. 응답에는 업로드 원문, AI 프롬프트, API 키, 모델 요청 본문을 넣지 않습니다.

### 오류 응답

```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "파일은 10MB 이하여야 합니다.",
    "action": "파일 크기를 줄인 뒤 다시 업로드해 주세요."
  }
}
```

| 상황 | 상태 코드 | 대표 코드 |
| --- | --- | --- |
| 요청에서 파일 누락 또는 잘못된 multipart 형식 | 422 | `INVALID_REQUEST` |
| TXT가 아닌 파일 | 415 | `UNSUPPORTED_FILE_TYPE` |
| 10MB 초과 | 413 | `FILE_TOO_LARGE` |
| 빈 파일·공백만 있음·지원 인코딩 아님 | 422 | `EMPTY_DOCUMENT`, `UNREADABLE_DOCUMENT` |
| AI 설정 누락·잘못된 주소 | 503 | `AI_CONFIGURATION_MISSING`, `AI_CONFIGURATION_INVALID` |
| AI 연결·시간 초과·사용 불가 응답 | 502 | `AI_CONNECTION_FAILED`, `AI_TIMEOUT`, `AI_PROVIDER_TEMPORARY_ERROR` 등 |
| 예상하지 못한 서버 오류 | 500 | 일반 서버 오류 응답 |

민감한 원문과 제공자 응답 본문은 오류 메시지와 로그에 남기지 않습니다. 일시적인 AI 오류나 결과 형식 오류는 workflow에서 최대 한 번 재시도한 후 실패 응답으로 종료합니다.

## 3. 상태 확인

| 항목 | 내용 |
| --- | --- |
| Method | `GET` |
| Endpoint | `/api/health` |
| 성공 응답 | `200 OK`, `{"status":"ok"}` |
| 용도 | Backend 프로세스가 요청을 받을 수 있는지 확인. 외부 AI 연결 상태는 검사하지 않음 |

## 4. 데이터 보존

- 분석 이력, 분석 ID, 데이터베이스, 파일 영구 저장은 MVP에서 사용하지 않습니다.
- 요청이 끝나면 업로드 파일을 닫습니다. 결과는 브라우저 화면의 현재 상태에서만 확인합니다.
- 분석을 위해 원문이 설정된 외부 AI 서비스로 전송됩니다. 외부 전송·보관 조건은 실제 서비스를 선택하기 전에 팀이 확인해야 합니다.

## 확인과 판정

- 판정: 확인 필요
- 근거: 단일 동기 분석 API와 입력·응답·오류 계약을 정리했습니다. 외부 AI 제공자별 호환성과 10MB의 정확한 바이트 기준은 아직 선택·확정되지 않았습니다.
- 실행 검증: 해당 없음. 명세 문서이며 API 테스트를 실행하지 않았습니다.
- 다음 권장 작업: 외부 AI 제공자를 결정한 뒤 실제 오류 응답과 모델별 출력 형식을 확인합니다.
