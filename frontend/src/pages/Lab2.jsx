import React, { useState } from "react";
import { hashString, hashFile, verifyFile } from "../api/backend.js";
import ResultCard from "../components/ResultCard.jsx";

export default function Lab2() {
  const [activeTab, setActiveTab] = useState("string"); // string, file, verify
  const [inputText, setInputText] = useState("");
  const [stringResult, setStringResult] = useState(null);
  const [fileResult, setFileResult] = useState(null);
  const [verifyResult, setVerifyResult] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [verifyFile, setVerifyFile] = useState(null);
  const [expectedHash, setExpectedHash] = useState("");
  const [loading, setLoading] = useState(false);

  // RFC 1321 test vectors for quick testing
  const testVectors = [
    { text: "", hash: "D41D8CD98F00B204E9800998ECF8427E" },
    { text: "a", hash: "0CC175B9C0F1B6A831C399E269772661" },
    { text: "abc", hash: "900150983CD24FB0D6963F7D28E17F72" },
    { text: "message digest", hash: "F96B697D7CB7938D525A2F31AAF161D0" },
    { text: "abcdefghijklmnopqrstuvwxyz", hash: "C3FCD3D76192E4007DFB496CCA67E13B" },
    { text: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", hash: "D174AB98D277D9F5A5611C2C9F419D9F" },
    { text: "12345678901234567890123456789012345678901234567890123456789012345678901234567890", hash: "57EDF4A22BE3C955AC49DA2E2107B67A" }
  ];

  const handleHashString = async () => {
    if (!inputText && inputText !== "") {
      alert("Будь ласка, введіть текст!");
      return;
    }

    setLoading(true);
    try {
      const result = await hashString(inputText);
      setStringResult(result);
    } catch (error) {
      alert("Помилка при обчисленні хешу: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleHashFile = async () => {
    if (!selectedFile) {
      alert("Будь ласка, оберіть файл!");
      return;
    }

    setLoading(true);
    try {
      const result = await hashFile(selectedFile);
      setFileResult(result);
    } catch (error) {
      alert("Помилка при обчисленні хешу файлу: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyFile = async () => {
    if (!verifyFile) {
      alert("Будь ласка, оберіть файл для перевірки!");
      return;
    }
    if (!expectedHash.trim()) {
      alert("Будь ласка, введіть очікуваний MD5 хеш!");
      return;
    }

    setLoading(true);
    try {
      const result = await verifyFile(verifyFile, expectedHash.trim());
      setVerifyResult(result);
    } catch (error) {
      alert("Помилка при перевірці файлу: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveResults = async () => {
    let content = "";
    const timestamp = new Date().toLocaleString();

    content += `MD5 Hash Results\n`;
    content += `Generated: ${timestamp}\n`;
    content += `${"=".repeat(80)}\n\n`;

    if (stringResult && activeTab === "string") {
      content += `STRING HASH:\n`;
      content += `-`.repeat(80) + `\n`;
      content += `Input: ${stringResult.text}\n`;
      content += `MD5 Hash: ${stringResult.hash}\n\n`;
    }

    if (fileResult && activeTab === "file") {
      content += `FILE HASH:\n`;
      content += `-`.repeat(80) + `\n`;
      content += `Filename: ${fileResult.filename}\n`;
      content += `Size: ${fileResult.size} bytes\n`;
      content += `MD5 Hash: ${fileResult.hash}\n\n`;
    }

    if (verifyResult && activeTab === "verify") {
      content += `FILE INTEGRITY VERIFICATION:\n`;
      content += `-`.repeat(80) + `\n`;
      content += `Filename: ${verifyResult.filename}\n`;
      content += `Size: ${verifyResult.size} bytes\n`;
      content += `Expected Hash: ${verifyResult.expected_hash}\n`;
      content += `Actual Hash: ${verifyResult.actual_hash}\n`;
      content += `Status: ${verifyResult.is_valid ? "✓ VALID" : "✗ INVALID"}\n`;
      content += `Message: ${verifyResult.message}\n\n`;
    }

    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const filename = `md5_results_${Date.now()}.txt`;

    // Try to use File System Access API if available (Chrome, Edge)
    if (window.showSaveFilePicker) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: filename,
          types: [{
            description: 'Text Files',
            accept: { 'text/plain': ['.txt'] },
          }],
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        alert('Файл успішно збережено!');
        return;
      } catch (err) {
        // User cancelled or error occurred
        if (err.name !== 'AbortError') {
          console.error('Error saving file:', err);
        }
        return;
      }
    }

    // Fallback to traditional download for browsers without File System Access API
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const loadTestVector = (testVector) => {
    setInputText(testVector.text);
    setStringResult(null);
  };

  return (
    <div className="page-container">
      <h2>Лабораторна №2 — MD5 Hash Algorithm</h2>

      {/* Tab Navigation */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px", borderBottom: "2px solid #ddd", paddingBottom: "10px" }}>
        <button
          onClick={() => setActiveTab("string")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "string" ? "#007bff" : "#f0f0f0",
            color: activeTab === "string" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "string" ? "bold" : "normal"
          }}
        >
          Хешування рядка
        </button>
        <button
          onClick={() => setActiveTab("file")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "file" ? "#007bff" : "#f0f0f0",
            color: activeTab === "file" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "file" ? "bold" : "normal"
          }}
        >
          Хешування файлу
        </button>
        <button
          onClick={() => setActiveTab("verify")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "verify" ? "#007bff" : "#f0f0f0",
            color: activeTab === "verify" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "verify" ? "bold" : "normal"
          }}
        >
          Перевірка цілісності
        </button>
      </div>

      {/* String Hash Tab */}
      {activeTab === "string" && (
        <div>
          <div className="form-container">
            <h3>Обчислення MD5 хешу рядка</h3>
            <div style={{ marginBottom: "15px" }}>
              <label>Введіть текст:</label>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                rows="5"
                style={{
                  width: "100%",
                  padding: "10px",
                  marginTop: "5px",
                  fontFamily: "monospace",
                  fontSize: "14px"
                }}
                placeholder="Введіть текст для хешування..."
              />
            </div>
            <button
              onClick={handleHashString}
              disabled={loading}
              style={{
                padding: "10px 20px",
                fontSize: "16px",
                backgroundColor: "#28a745",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: loading ? "not-allowed" : "pointer"
              }}
            >
              {loading ? "Обчислення..." : "Обчислити MD5"}
            </button>
          </div>

          {/* RFC 1321 Test Vectors */}
          <div className="form-container" style={{ marginTop: "20px" }}>
            <h3>Тестові значення (RFC 1321)</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
              {testVectors.map((tv, index) => (
                <div
                  key={index}
                  onClick={() => loadTestVector(tv)}
                  style={{
                    padding: "10px",
                    border: "1px solid #ddd",
                    borderRadius: "4px",
                    cursor: "pointer",
                    backgroundColor: "#f9f9f9",
                    transition: "background-color 0.2s"
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = "#e9ecef"}
                  onMouseLeave={(e) => e.target.style.backgroundColor = "#f9f9f9"}
                >
                  <div style={{ fontFamily: "monospace", fontSize: "12px", marginBottom: "5px", color: "#666" }}>
                    H({tv.text === "" ? "(порожній рядок)" : tv.text.length > 30 ? tv.text.substring(0, 30) + "..." : `"${tv.text}"`})
                  </div>
                  <div style={{ fontFamily: "monospace", fontSize: "11px", color: "#007bff" }}>
                    {tv.hash}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {stringResult && stringResult.success && (
            <>
              <ResultCard
                title="Вхідний текст"
                value={stringResult.text || "(порожній рядок)"}
              />
              <ResultCard
                title="MD5 Hash (uppercase)"
                value={stringResult.hash}
              />
              <ResultCard
                title="MD5 Hash (lowercase)"
                value={stringResult.hash_lower}
              />
              <button
                onClick={handleSaveResults}
                style={{
                  padding: "10px 20px",
                  fontSize: "16px",
                  backgroundColor: "#17a2b8",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  marginTop: "10px"
                }}
              >
                Зберегти результат у файл
              </button>
            </>
          )}
        </div>
      )}

      {/* File Hash Tab */}
      {activeTab === "file" && (
        <div>
          <div className="form-container">
            <h3>Обчислення MD5 хешу файлу</h3>
            <div style={{ marginBottom: "15px" }}>
              <label>Оберіть файл:</label>
              <input
                type="file"
                onChange={(e) => setSelectedFile(e.target.files[0])}
                style={{ marginTop: "10px", display: "block" }}
              />
              {selectedFile && (
                <div style={{ marginTop: "10px", color: "#666", fontSize: "14px" }}>
                  Обраний файл: <strong>{selectedFile.name}</strong> ({(selectedFile.size / 1024).toFixed(2)} KB)
                </div>
              )}
            </div>
            <button
              onClick={handleHashFile}
              disabled={loading || !selectedFile}
              style={{
                padding: "10px 20px",
                fontSize: "16px",
                backgroundColor: "#28a745",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: loading || !selectedFile ? "not-allowed" : "pointer"
              }}
            >
              {loading ? "Обчислення..." : "Обчислити MD5 файлу"}
            </button>
          </div>

          {fileResult && fileResult.success && (
            <>
              <ResultCard
                title="Ім'я файлу"
                value={fileResult.filename}
              />
              <ResultCard
                title="Розмір файлу"
                value={`${fileResult.size} bytes (${(fileResult.size / 1024).toFixed(2)} KB)`}
              />
              <ResultCard
                title="MD5 Hash (uppercase)"
                value={fileResult.hash}
              />
              <ResultCard
                title="MD5 Hash (lowercase)"
                value={fileResult.hash_lower}
              />
              <button
                onClick={handleSaveResults}
                style={{
                  padding: "10px 20px",
                  fontSize: "16px",
                  backgroundColor: "#17a2b8",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  marginTop: "10px"
                }}
              >
                Зберегти результат у файл
              </button>
            </>
          )}
        </div>
      )}

      {/* Verify File Tab */}
      {activeTab === "verify" && (
        <div>
          <div className="form-container">
            <h3>Перевірка цілісності файлу</h3>
            <div style={{ marginBottom: "15px" }}>
              <label>Оберіть файл для перевірки:</label>
              <input
                type="file"
                onChange={(e) => setVerifyFile(e.target.files[0])}
                style={{ marginTop: "10px", display: "block" }}
              />
              {verifyFile && (
                <div style={{ marginTop: "10px", color: "#666", fontSize: "14px" }}>
                  Обраний файл: <strong>{verifyFile.name}</strong> ({(verifyFile.size / 1024).toFixed(2)} KB)
                </div>
              )}
            </div>
            <div style={{ marginBottom: "15px" }}>
              <label>Введіть очікуваний MD5 хеш (32 символи):</label>
              <input
                type="text"
                value={expectedHash}
                onChange={(e) => setExpectedHash(e.target.value)}
                placeholder="Наприклад: D41D8CD98F00B204E9800998ECF8427E"
                style={{
                  width: "100%",
                  padding: "10px",
                  marginTop: "5px",
                  fontFamily: "monospace",
                  fontSize: "14px"
                }}
                maxLength={32}
              />
              <small style={{ color: "#666" }}>
                Введено символів: {expectedHash.length}/32
              </small>
            </div>
            <button
              onClick={handleVerifyFile}
              disabled={loading || !verifyFile || expectedHash.length !== 32}
              style={{
                padding: "10px 20px",
                fontSize: "16px",
                backgroundColor: "#28a745",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: loading || !verifyFile || expectedHash.length !== 32 ? "not-allowed" : "pointer"
              }}
            >
              {loading ? "Перевірка..." : "Перевірити цілісність"}
            </button>
          </div>

          {verifyResult && verifyResult.success && (
            <>
              <ResultCard
                title="Ім'я файлу"
                value={verifyResult.filename}
              />
              <ResultCard
                title="Розмір файлу"
                value={`${verifyResult.size} bytes (${(verifyResult.size / 1024).toFixed(2)} KB)`}
              />
              <ResultCard
                title="Очікуваний Hash"
                value={verifyResult.expected_hash}
              />
              <ResultCard
                title="Фактичний Hash"
                value={verifyResult.actual_hash}
              />
              <div
                style={{
                  padding: "15px",
                  borderRadius: "8px",
                  backgroundColor: verifyResult.is_valid ? "#d4edda" : "#f8d7da",
                  border: `2px solid ${verifyResult.is_valid ? "#28a745" : "#dc3545"}`,
                  marginTop: "15px"
                }}
              >
                <h3 style={{ margin: "0 0 10px 0", color: verifyResult.is_valid ? "#155724" : "#721c24" }}>
                  {verifyResult.is_valid ? "✓ Файл є дійсним" : "✗ Файл змінений або пошкоджений"}
                </h3>
                <p style={{ margin: 0, color: verifyResult.is_valid ? "#155724" : "#721c24" }}>
                  {verifyResult.message}
                </p>
              </div>
              <button
                onClick={handleSaveResults}
                style={{
                  padding: "10px 20px",
                  fontSize: "16px",
                  backgroundColor: "#17a2b8",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  marginTop: "10px"
                }}
              >
                Зберегти результат у файл
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
