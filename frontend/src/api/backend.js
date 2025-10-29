const API_URL = "http://127.0.0.1:8000";

export async function generateNumbers(params = null) {
  const body = params ? JSON.stringify(params) : null;
  const headers = params ? { "Content-Type": "application/json" } : {};

  const response = await fetch(`${API_URL}/lab1/generate/`, {
    method: "POST",
    headers,
    body
  });
  return response.json();
}

