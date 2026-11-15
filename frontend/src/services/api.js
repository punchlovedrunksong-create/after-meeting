const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

export async function submitAnalysis(file) {
  const formData = new FormData();
  formData.append("file", file);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/v1/analyses`, {
      method: "POST",
      body: formData,
    });
  } catch {
    const error = new Error("Backend 서버에 연결할 수 없습니다.");
    error.action = "Backend가 실행 중인지 확인한 뒤 다시 시도해 주세요.";
    throw error;
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.error ?? payload.detail ?? {};
    const error = new Error(detail.message ?? "분석 요청을 처리하지 못했습니다.");
    error.action = detail.action ?? "잠시 후 다시 시도해 주세요.";
    throw error;
  }
  return payload;
}
