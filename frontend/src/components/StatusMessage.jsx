export default function StatusMessage({ status, error }) {
  if (status === "idle") return null;
  if (status === "processing") {
    return <div className="status-placeholder" role="status">회의 내용을 분석하고 있습니다…</div>;
  }
  if (status === "success") {
    return <div className="status-success" role="status">분석이 완료되었습니다. 원문과 대조해 결과를 확인해 주세요.</div>;
  }
  return (
    <div className="status-error" role="alert">
      <strong>{error?.message}</strong>
      {error?.action && <p>{error.action}</p>}
    </div>
  );
}
