const API_URL = "http://127.0.0.1:8000";

// ==================== LAB 1 API ====================

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

// ==================== LAB 2 API ====================

export async function hashString(text) {
  const response = await fetch(`${API_URL}/lab2/hash-string/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });
  return response.json();
}

export async function hashFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/lab2/hash-file/`, {
    method: "POST",
    body: formData
  });
  return response.json();
}

export async function verifyFile(file, expectedHash) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("expected_hash", expectedHash);

  const response = await fetch(`${API_URL}/lab2/verify-file/`, {
    method: "POST",
    body: formData
  });
  return response.json();
}

