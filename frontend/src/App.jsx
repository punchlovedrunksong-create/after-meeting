import FileUpload from "./components/FileUpload.jsx";
import SummaryResult from "./components/SummaryResult.jsx";
import TodoList from "./components/TodoList.jsx";
import StatusMessage from "./components/StatusMessage.jsx";
import { submitAnalysis } from "./services/api.js";
import { useState } from "react";

export default function App() {
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  async function handleSubmit(file) {
    setStatus("processing");
    setError(null);
    setAnalysis(null);
    try {
      const result = await submitAnalysis(file);
      setAnalysis(result);
      setStatus("success");
    } catch (requestError) {
      setError({
        message: requestError.message || "분석 중 오류가 발생했습니다.",
        action: requestError.action || "잠시 후 다시 시도해 주세요.",
      });
      setStatus("error");
    }
  }

  return (
    <main className="page-shell">
      <header className="page-header">
        <p className="eyebrow">AFTER MEETING</p>
        <h1>미팅 후속 업무 정리</h1>
        <p className="intro">
          이미 텍스트로 변환된 회의 내용을 요약하고 할 일을 정리합니다.
        </p>
      </header>

      <FileUpload onSubmit={handleSubmit} busy={status === "processing"} />
      <StatusMessage status={status} error={error} />
      <section className="results-grid" aria-label="분석 결과 자리">
        <SummaryResult summary={analysis?.summary} />
        <TodoList todos={analysis?.todos} />
      </section>
    </main>
  );
}
