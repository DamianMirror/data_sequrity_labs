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

// ==================== LAB 3 API ====================

export async function deriveKey(passphrase) {
  const response = await fetch(`${API_URL}/lab3/derive-key/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ passphrase })
  });
  return response.json();
}

export async function encryptFile(file, passphrase) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("passphrase", passphrase);

  const response = await fetch(`${API_URL}/lab3/encrypt-file/`, {
    method: "POST",
    body: formData
  });
  return response.json();
}

export async function decryptFile(file, passphrase) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("passphrase", passphrase);

  const response = await fetch(`${API_URL}/lab3/decrypt-file/`, {
    method: "POST",
    body: formData
  });
  return response.json();
}

// ==================== LAB 4 API ====================

export async function generateRSAKeys(keySize = 2048) {
  const response = await fetch(`${API_URL}/lab4/generate-keys/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key_size: keySize })
  });
  return response.json();
}

export async function encryptRSAFile(file, publicKeyPem) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("public_key_pem", publicKeyPem);

  const response = await fetch(`${API_URL}/lab4/encrypt-file/`, {
    method: "POST",
    body: formData
  });
  return response.json();
}

export async function decryptRSAFile(file, privateKeyPem) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("private_key_pem", privateKeyPem);

  const response = await fetch(`${API_URL}/lab4/decrypt-file/`, {
    method: "POST",
    body: formData
  });
  return response.json();
}

export async function comparePerformance(fileSizeKb = 100) {
  const response = await fetch(`${API_URL}/lab4/compare-performance/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ file_size_kb: fileSizeKb })
  });
  return response.json();
}

