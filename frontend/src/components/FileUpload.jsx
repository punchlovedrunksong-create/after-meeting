import { useState } from "react";

const MAX_FILE_BYTES = 10 * 1024 * 1024;

export default function FileUpload({ onSubmit, busy }) {
  const [file, setFile] = useState(null);
  const [localError, setLocalError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    setLocalError("");
    if (!file) {
      setLocalError("분석할 TXT 파일을 선택해 주세요.");
      return;
    }
    if (!file.name.toLowerCase().endsWith(".txt")) {
      setLocalError("TXT 파일만 업로드할 수 있습니다.");
      return;
    }
    if (file.size > MAX_FILE_BYTES) {
      setLocalError("파일은 10MB 이하여야 합니다.");
      return;
    }
    onSubmit(file);
  }

  return (
    <section className="panel upload-panel" aria-labelledby="upload-title">
      <form className="upload-form" onSubmit={handleSubmit}>
        <p className="eyebrow">INPUT</p>
        <h2 id="upload-title">회의 TXT 파일</h2>
        <p>이미 STT로 추출된 회의 텍스트를 업로드하세요. 최대 10MB.</p>
        <div className="upload-controls">
          <input
            type="file"
            accept=".txt,text/plain"
            disabled={busy}
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
              setLocalError("");
            }}
            aria-label="회의 TXT 파일 선택"
          />
          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? "분석 중…" : "요약 및 투두 생성"}
          </button>
        </div>
        {file && <p className="file-meta">선택됨: {file.name}</p>}
        {localError && <p className="inline-error" role="alert">{localError}</p>}
      </form>
    </section>
  );
}
