const sections = [
  ["회의 안건", "meeting_agenda"],
  ["문제점", "issues"],
  ["해결방안", "solutions"],
  ["결론", "conclusion"],
];

export default function SummaryResult({ summary }) {
  return (
    <section className="panel" aria-labelledby="summary-title">
      <p className="eyebrow">SUMMARY</p>
      <h2 id="summary-title">회의 요약</h2>
      {!summary ? (
        <p className="placeholder">TXT 파일을 분석하면 요약이 여기에 표시됩니다.</p>
      ) : (
        <div className="summary-sections">
          {sections.map(([label, key]) => (
            <div className="summary-item" key={key}>
              <h3>{label}</h3>
              <p className={summary[key] ? "summary-text" : "placeholder"}>
                {summary[key] || "원문에서 확인되지 않음"}
              </p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
