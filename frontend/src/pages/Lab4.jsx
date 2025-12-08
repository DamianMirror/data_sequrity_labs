import React, { useState } from "react";
import { generateRSAKeys, encryptRSAFile, decryptRSAFile, comparePerformance } from "../api/backend.js";
import ResultCard from "../components/ResultCard.jsx";

export default function Lab4() {
  const [activeTab, setActiveTab] = useState("keys"); // keys, encrypt, decrypt, compare
  const [keySize, setKeySize] = useState(2048);
  const [keys, setKeys] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [encryptedFile, setEncryptedFile] = useState(null);
  const [publicKeyInput, setPublicKeyInput] = useState("");
  const [privateKeyInput, setPrivateKeyInput] = useState("");
  const [encryptResult, setEncryptResult] = useState(null);
  const [decryptResult, setDecryptResult] = useState(null);
  const [comparisonFileSize, setComparisonFileSize] = useState(100);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerateKeys = async () => {
    setLoading(true);
    try {
      const result = await generateRSAKeys(keySize);
      if (result.success) {
        setKeys(result);
        setPublicKeyInput(result.public_key_pem);
        setPrivateKeyInput(result.private_key_pem);
      } else {
        alert("Помилка при генерації ключів: " + result.error);
      }
    } catch (error) {
      alert("Помилка при генерації ключів: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEncryptFile = async () => {
    if (!selectedFile) {
      alert("Будь ласка, оберіть файл для шифрування!");
      return;
    }
    if (!publicKeyInput.trim()) {
      alert("Будь ласка, згенерируйте або введіть публічний ключ!");
      return;
    }

    setLoading(true);
    try {
      const result = await encryptRSAFile(selectedFile, publicKeyInput);
      if (result.success) {
        setEncryptResult(result);
      } else {
        alert("Помилка при шифруванні файлу: " + result.error);
      }
    } catch (error) {
      alert("Помилка при шифруванні файлу: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDecryptFile = async () => {
    if (!encryptedFile) {
      alert("Будь ласка, оберіть зашифрований файл!");
      return;
    }
    if (!privateKeyInput.trim()) {
      alert("Будь ласка, згенерируйте або введіть приватний ключ!");
      return;
    }

    setLoading(true);
    try {
      const result = await decryptRSAFile(encryptedFile, privateKeyInput);
      if (result.success) {
        setDecryptResult(result);
      } else {
        alert("Помилка при дешифруванні файлу: " + result.error);
      }
    } catch (error) {
      alert("Помилка при дешифруванні файлу: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleComparePerformance = async () => {
    setLoading(true);
    try {
      const result = await comparePerformance(comparisonFileSize);
      if (result.success) {
        setComparisonResult(result);
      } else {
        alert("Помилка при порівнянні: " + result.error);
      }
    } catch (error) {
      alert("Помилка при порівнянні: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadEncryptedFile = async () => {
    if (!encryptResult || !encryptResult.encrypted_data) return;

    const binaryString = atob(encryptResult.encrypted_data);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    const blob = new Blob([bytes], { type: "application/octet-stream" });
    const filename = encryptResult.filename + ".rsa";

    if (window.showSaveFilePicker) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: filename,
          types: [{
            description: 'RSA Encrypted Files',
            accept: { 'application/octet-stream': ['.rsa'] },
          }],
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        alert('Зашифрований файл успішно збережено!');
        return;
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Error saving file:', err);
        }
        return;
      }
    }

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const downloadDecryptedFile = async () => {
    if (!decryptResult || !decryptResult.decrypted_data) return;

    const binaryString = atob(decryptResult.decrypted_data);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    const blob = new Blob([bytes], { type: "application/octet-stream" });
    const originalName = decryptResult.filename.replace('.rsa', '');

    if (window.showSaveFilePicker) {
      try {
        const lastDotIndex = originalName.lastIndexOf('.');
        const extension = lastDotIndex !== -1 ? originalName.substring(lastDotIndex) : '';

        const handle = await window.showSaveFilePicker({
          suggestedName: originalName,
          types: [{
            description: 'Decrypted File',
            accept: { 'application/octet-stream': extension ? [extension] : [] },
          }],
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        alert('Дешифрований файл успішно збережено!');
        return;
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Error saving file:', err);
        }
        return;
      }
    }

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = originalName;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const downloadKeys = async (keyType) => {
    if (!keys) return;

    const keyData = keyType === 'private' ? keys.private_key_pem : keys.public_key_pem;
    const blob = new Blob([keyData], { type: "text/plain;charset=utf-8" });
    const filename = `rsa_${keyType}_key_${keys.key_size}.pem`;

    if (window.showSaveFilePicker) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: filename,
          types: [{
            description: 'PEM Key Files',
            accept: { 'application/x-pem-file': ['.pem'] },
          }],
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        alert('Ключ успішно збережено!');
        return;
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Error saving file:', err);
        }
        return;
      }
    }

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const downloadComparisonReport = async () => {
    if (!comparisonResult || !comparisonResult.report) return;

    const blob = new Blob([comparisonResult.report], { type: "text/plain;charset=utf-8" });
    const filename = `rsa_rc5_comparison_${comparisonFileSize}kb_${Date.now()}.txt`;

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
        alert('Звіт успішно збережено!');
        return;
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Error saving file:', err);
        }
        return;
      }
    }

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return (
    <div className="page-container">
      <h2>Лабораторна №4 — RSA Encryption</h2>

      {/* Tab Navigation */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px", borderBottom: "2px solid #ddd", paddingBottom: "10px" }}>
        <button
          onClick={() => setActiveTab("keys")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "keys" ? "#007bff" : "#f0f0f0",
            color: activeTab === "keys" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "keys" ? "bold" : "normal"
          }}
        >
          Генерація ключів
        </button>
        <button
          onClick={() => setActiveTab("encrypt")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "encrypt" ? "#007bff" : "#f0f0f0",
            color: activeTab === "encrypt" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "encrypt" ? "bold" : "normal"
          }}
        >
          Шифрування файлу
        </button>
        <button
          onClick={() => setActiveTab("decrypt")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "decrypt" ? "#007bff" : "#f0f0f0",
            color: activeTab === "decrypt" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "decrypt" ? "bold" : "normal"
          }}
        >
          Дешифрування файлу
        </button>
        <button
          onClick={() => setActiveTab("compare")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "compare" ? "#007bff" : "#f0f0f0",
            color: activeTab === "compare" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "compare" ? "bold" : "normal"
          }}
        >
          Порівняння RSA vs RC5
        </button>
      </div>

      {/* Key Generation Tab */}
      {activeTab === "keys" && (
        <div>
          <div className="form-container">
            <h3>Генерація RSA ключів</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Згенерируйте пару RSA ключів (приватний та публічний) для шифрування файлів.
            </p>
            <div style={{ marginBottom: "15px" }}>
              <label>Розмір ключа (біт):</label>
              <select
                value={keySize}
                onChange={(e) => setKeySize(parseInt(e.target.value))}
                style={{
                  width: "100%",
                  padding: "10px",
                  marginTop: "5px",
                  fontSize: "14px"
                }}
              >
                <option value={1024}>1024 біт (швидкий, менш безпечний)</option>
                <option value={2048}>2048 біт (рекомендовано)</option>
                <option value={4096}>4096 біт (дуже безпечний, повільний)</option>
              </select>
            </div>
            <button
              onClick={handleGenerateKeys}
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
              {loading ? "Генерація..." : "Згенерувати ключі"}
            </button>
          </div>

          {keys && keys.success && (
            <>
              <ResultCard
                title="Розмір ключа"
                value={`${keys.key_size} біт`}
              />
              <div style={{ marginTop: "15px", padding: "15px", borderRadius: "8px", backgroundColor: "#f8f9fa", border: "1px solid #dee2e6" }}>
                <h4 style={{ marginTop: 0 }}>Публічний ключ (для шифрування):</h4>
                <textarea
                  value={keys.public_key_pem}
                  readOnly
                  style={{
                    width: "100%",
                    height: "120px",
                    fontFamily: "monospace",
                    fontSize: "12px",
                    padding: "10px",
                    resize: "vertical"
                  }}
                />
                <button
                  onClick={() => downloadKeys('public')}
                  style={{
                    padding: "8px 16px",
                    fontSize: "14px",
                    backgroundColor: "#17a2b8",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    marginTop: "10px"
                  }}
                >
                  Зберегти публічний ключ
                </button>
              </div>
              <div style={{ marginTop: "15px", padding: "15px", borderRadius: "8px", backgroundColor: "#f8f9fa", border: "1px solid #dee2e6" }}>
                <h4 style={{ marginTop: 0 }}>Приватний ключ (для дешифрування):</h4>
                <textarea
                  value={keys.private_key_pem}
                  readOnly
                  style={{
                    width: "100%",
                    height: "120px",
                    fontFamily: "monospace",
                    fontSize: "12px",
                    padding: "10px",
                    resize: "vertical"
                  }}
                />
                <button
                  onClick={() => downloadKeys('private')}
                  style={{
                    padding: "8px 16px",
                    fontSize: "14px",
                    backgroundColor: "#dc3545",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    marginTop: "10px"
                  }}
                >
                  Зберегти приватний ключ
                </button>
                <p style={{ marginTop: "10px", color: "#dc3545", fontSize: "14px" }}>
                  ⚠️ Зберігайте приватний ключ у безпечному місці! Без нього ви не зможете дешифрувати файли.
                </p>
              </div>
            </>
          )}
        </div>
      )}

      {/* Encrypt File Tab */}
      {activeTab === "encrypt" && (
        <div>
          <div className="form-container">
            <h3>Шифрування файлу за допомогою RSA</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Файл розбивається на блоки і кожен блок шифрується окремо за допомогою RSA-2048.
            </p>
            <div style={{ marginBottom: "15px" }}>
              <label>Оберіть файл для шифрування:</label>
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
            <div style={{ marginBottom: "15px" }}>
              <label>Публічний ключ RSA (PEM формат):</label>
              <textarea
                value={publicKeyInput}
                onChange={(e) => setPublicKeyInput(e.target.value)}
                placeholder="Вставте публічний ключ або згенерируйте новий на вкладці 'Генерація ключів'"
                style={{
                  width: "100%",
                  height: "100px",
                  fontFamily: "monospace",
                  fontSize: "12px",
                  padding: "10px",
                  marginTop: "5px",
                  resize: "vertical"
                }}
              />
            </div>
            <button
              onClick={handleEncryptFile}
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
              {loading ? "Шифрування..." : "Зашифрувати файл"}
            </button>
          </div>

          {encryptResult && encryptResult.success && (
            <>
              <ResultCard
                title="Ім'я файлу"
                value={encryptResult.filename}
              />
              <ResultCard
                title="Оригінальний розмір"
                value={`${encryptResult.original_size} bytes`}
              />
              <ResultCard
                title="Розмір після padding"
                value={`${encryptResult.padded_size} bytes`}
              />
              <ResultCard
                title="Розмір зашифрованого файлу"
                value={`${encryptResult.encrypted_size} bytes`}
              />
              <ResultCard
                title="Час шифрування"
                value={`${encryptResult.encryption_time.toFixed(6)} секунд`}
              />
              <div
                style={{
                  padding: "15px",
                  borderRadius: "8px",
                  backgroundColor: "#d4edda",
                  border: "2px solid #28a745",
                  marginTop: "15px"
                }}
              >
                <h3 style={{ margin: "0 0 10px 0", color: "#155724" }}>
                  ✓ Файл успішно зашифровано
                </h3>
                <p style={{ margin: 0, color: "#155724" }}>
                  Натисніть кнопку нижче, щоб завантажити зашифрований файл
                </p>
              </div>
              <button
                onClick={downloadEncryptedFile}
                style={{
                  padding: "10px 20px",
                  fontSize: "16px",
                  backgroundColor: "#007bff",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  marginTop: "10px"
                }}
              >
                Завантажити зашифрований файл
              </button>
            </>
          )}
        </div>
      )}

      {/* Decrypt File Tab */}
      {activeTab === "decrypt" && (
        <div>
          <div className="form-container">
            <h3>Дешифрування файлу RSA</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Завантажте зашифрований файл та введіть приватний ключ для дешифрування.
            </p>
            <div style={{ marginBottom: "15px" }}>
              <label>Оберіть зашифрований файл:</label>
              <input
                type="file"
                onChange={(e) => setEncryptedFile(e.target.files[0])}
                style={{ marginTop: "10px", display: "block" }}
              />
              {encryptedFile && (
                <div style={{ marginTop: "10px", color: "#666", fontSize: "14px" }}>
                  Обраний файл: <strong>{encryptedFile.name}</strong> ({(encryptedFile.size / 1024).toFixed(2)} KB)
                </div>
              )}
            </div>
            <div style={{ marginBottom: "15px" }}>
              <label>Приватний ключ RSA (PEM формат):</label>
              <textarea
                value={privateKeyInput}
                onChange={(e) => setPrivateKeyInput(e.target.value)}
                placeholder="Вставте приватний ключ або згенерируйте новий на вкладці 'Генерація ключів'"
                style={{
                  width: "100%",
                  height: "100px",
                  fontFamily: "monospace",
                  fontSize: "12px",
                  padding: "10px",
                  marginTop: "5px",
                  resize: "vertical"
                }}
              />
            </div>
            <button
              onClick={handleDecryptFile}
              disabled={loading || !encryptedFile}
              style={{
                padding: "10px 20px",
                fontSize: "16px",
                backgroundColor: "#28a745",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: loading || !encryptedFile ? "not-allowed" : "pointer"
              }}
            >
              {loading ? "Дешифрування..." : "Дешифрувати файл"}
            </button>
          </div>

          {decryptResult && decryptResult.success && (
            <>
              <ResultCard
                title="Ім'я файлу"
                value={decryptResult.filename}
              />
              <ResultCard
                title="Розмір зашифрованого файлу"
                value={`${decryptResult.encrypted_size} bytes`}
              />
              <ResultCard
                title="Розмір дешифрованого файлу"
                value={`${decryptResult.decrypted_size} bytes`}
              />
              <ResultCard
                title="Час дешифрування"
                value={`${decryptResult.decryption_time.toFixed(6)} секунд`}
              />
              <div
                style={{
                  padding: "15px",
                  borderRadius: "8px",
                  backgroundColor: "#d4edda",
                  border: "2px solid #28a745",
                  marginTop: "15px"
                }}
              >
                <h3 style={{ margin: "0 0 10px 0", color: "#155724" }}>
                  ✓ Файл успішно дешифровано
                </h3>
                <p style={{ margin: 0, color: "#155724" }}>
                  Натисніть кнопку нижче, щоб завантажити дешифрований файл
                </p>
              </div>
              <button
                onClick={downloadDecryptedFile}
                style={{
                  padding: "10px 20px",
                  fontSize: "16px",
                  backgroundColor: "#007bff",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  marginTop: "10px"
                }}
              >
                Завантажити дешифрований файл
              </button>
            </>
          )}
        </div>
      )}

      {/* Performance Comparison Tab */}
      {activeTab === "compare" && (
        <div>
          <div className="form-container">
            <h3>Порівняння продуктивності: RSA vs RC5</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Порівняйте швидкість шифрування між чистим RSA та RC5.
            </p>
            <div style={{ marginBottom: "15px" }}>
              <label>Розмір тестового файлу (KB):</label>
              <select
                value={comparisonFileSize}
                onChange={(e) => setComparisonFileSize(parseInt(e.target.value))}
                style={{
                  width: "100%",
                  padding: "10px",
                  marginTop: "5px",
                  fontSize: "14px"
                }}
              >
                <option value={10}>10 KB</option>
                <option value={100}>100 KB</option>
                <option value={500}>500 KB</option>
                <option value={1000}>1 MB (1000 KB)</option>
              </select>
            </div>
            <button
              onClick={handleComparePerformance}
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
              {loading ? "Виконання порівняння..." : "Виконати порівняння"}
            </button>
          </div>

          {comparisonResult && comparisonResult.success && (
            <>
              <div style={{ marginTop: "20px", padding: "15px", borderRadius: "8px", backgroundColor: "#f8f9fa", border: "1px solid #dee2e6" }}>
                <h3>Результати порівняння</h3>
                <pre style={{
                  fontFamily: "monospace",
                  fontSize: "12px",
                  backgroundColor: "#fff",
                  padding: "15px",
                  borderRadius: "4px",
                  overflow: "auto",
                  maxHeight: "500px"
                }}>
                  {comparisonResult.report}
                </pre>
                <button
                  onClick={downloadComparisonReport}
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
                  Зберегти звіт
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}