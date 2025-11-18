import React, { useState } from "react";
import { deriveKey, encryptFile, decryptFile } from "../api/backend.js";
import ResultCard from "../components/ResultCard.jsx";

export default function Lab3() {
  const [activeTab, setActiveTab] = useState("key"); // key, encrypt, decrypt
  const [passphrase, setPassphrase] = useState("");
  const [keyInfo, setKeyInfo] = useState(null);
  const [encryptPassphrase, setEncryptPassphrase] = useState("");
  const [decryptPassphrase, setDecryptPassphrase] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [encryptedFile, setEncryptedFile] = useState(null);
  const [encryptResult, setEncryptResult] = useState(null);
  const [decryptResult, setDecryptResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleDeriveKey = async () => {
    if (!passphrase.trim()) {
      alert("Будь ласка, введіть парольну фразу!");
      return;
    }

    setLoading(true);
    try {
      const result = await deriveKey(passphrase);
      if (result.success) {
        setKeyInfo(result);
      } else {
        alert("Помилка при генерації ключа: " + result.error);
      }
    } catch (error) {
      alert("Помилка при генерації ключа: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEncryptFile = async () => {
    if (!selectedFile) {
      alert("Будь ласка, оберіть файл для шифрування!");
      return;
    }
    if (!encryptPassphrase.trim()) {
      alert("Будь ласка, введіть парольну фразу!");
      return;
    }

    setLoading(true);
    try {
      const result = await encryptFile(selectedFile, encryptPassphrase);
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
    if (!decryptPassphrase.trim()) {
      alert("Будь ласка, введіть парольну фразу!");
      return;
    }

    setLoading(true);
    try {
      const result = await decryptFile(encryptedFile, decryptPassphrase);
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

  const downloadEncryptedFile = async () => {
    if (!encryptResult || !encryptResult.encrypted_data) return;

    const binaryString = atob(encryptResult.encrypted_data);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    const blob = new Blob([bytes], { type: "application/octet-stream" });
    const filename = encryptResult.filename + ".enc";

    // Try to use File System Access API if available (Chrome, Edge)
    if (window.showSaveFilePicker) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: filename,
          types: [{
            description: 'Encrypted Files',
            accept: { 'application/octet-stream': ['.enc'] },
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

    // Fallback to traditional download for browsers without File System Access API
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
    const originalName = decryptResult.filename.replace('.enc', '');

    // Try to use File System Access API if available (Chrome, Edge)
    if (window.showSaveFilePicker) {
      try {
        // Extract file extension if present
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

    // Fallback to traditional download for browsers without File System Access API
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = originalName;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const handleSaveKeyInfo = async () => {
    if (!keyInfo) return;

    const timestamp = new Date().toLocaleString();
    let content = `RC5 Key Derivation Information\n`;
    content += `Generated: ${timestamp}\n`;
    content += `${"=".repeat(80)}\n\n`;
    content += `Passphrase: ${keyInfo.passphrase}\n`;
    content += `MD5(Passphrase): ${keyInfo.md5_passphrase}\n`;
    content += `MD5(MD5(Passphrase)): ${keyInfo.md5_of_md5}\n`;
    content += `Full Key (256-bit hex): ${keyInfo.full_key_hex}\n`;
    content += `Key Length: ${keyInfo.key_length_bits} bits\n`;

    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const filename = `rc5_key_info_${Date.now()}.txt`;

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
      <h2>Лабораторна №3 — RC5 File Encryption (CBC Mode)</h2>

      {/* Tab Navigation */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px", borderBottom: "2px solid #ddd", paddingBottom: "10px" }}>
        <button
          onClick={() => setActiveTab("key")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "key" ? "#007bff" : "#f0f0f0",
            color: activeTab === "key" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "key" ? "bold" : "normal"
          }}
        >
          Генерація ключа
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
      </div>

      {/* Key Derivation Tab */}
      {activeTab === "key" && (
        <div>
          <div className="form-container">
            <h3>Генерація ключа з парольної фрази</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Введіть парольну фразу, щоб згенерувати 256-бітний ключ для RC5 шифрування.
              Ключ генерується шляхом подвійного хешування MD5.
            </p>
            <div style={{ marginBottom: "15px" }}>
              <label>Парольна фраза:</label>
              <input
                type="password"
                value={passphrase}
                onChange={(e) => setPassphrase(e.target.value)}
                placeholder="Введіть парольну фразу..."
                style={{
                  width: "100%",
                  padding: "10px",
                  marginTop: "5px",
                  fontSize: "14px"
                }}
              />
            </div>
            <button
              onClick={handleDeriveKey}
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
              {loading ? "Генерація..." : "Згенерувати ключ"}
            </button>
          </div>

          {keyInfo && keyInfo.success && (
            <>
              <ResultCard
                title="Парольна фраза"
                value={keyInfo.passphrase}
              />
              <ResultCard
                title="MD5(Passphrase)"
                value={keyInfo.md5_passphrase}
              />
              <ResultCard
                title="MD5(MD5(Passphrase))"
                value={keyInfo.md5_of_md5}
              />
              <ResultCard
                title="Повний ключ (256-bit)"
                value={keyInfo.full_key_hex}
              />
              <ResultCard
                title="Довжина ключа"
                value={`${keyInfo.key_length_bits} біт`}
              />
              <button
                onClick={handleSaveKeyInfo}
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
                Зберегти інформацію про ключ
              </button>
            </>
          )}
        </div>
      )}

      {/* Encrypt File Tab */}
      {activeTab === "encrypt" && (
        <div>
          <div className="form-container">
            <h3>Шифрування файлу за допомогою RC5-32/12/16</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Шифрування виконується в режимі CBC (Cipher Block Chaining) з випадковим IV.
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
              <label>Парольна фраза для шифрування:</label>
              <input
                type="password"
                value={encryptPassphrase}
                onChange={(e) => setEncryptPassphrase(e.target.value)}
                placeholder="Введіть парольну фразу..."
                style={{
                  width: "100%",
                  padding: "10px",
                  marginTop: "5px",
                  fontSize: "14px"
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
                value={`${encryptResult.encrypted_size} bytes (з IV)`}
              />
              <ResultCard
                title="Кількість зашифрованих блоків"
                value={encryptResult.blocks_encrypted}
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
            <h3>Дешифрування файлу RC5-32/12/16</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Завантажте зашифрований файл та введіть правильну парольну фразу для дешифрування.
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
              <label>Парольна фраза для дешифрування:</label>
              <input
                type="password"
                value={decryptPassphrase}
                onChange={(e) => setDecryptPassphrase(e.target.value)}
                placeholder="Введіть парольну фразу..."
                style={{
                  width: "100%",
                  padding: "10px",
                  marginTop: "5px",
                  fontSize: "14px"
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
                title="Кількість дешифрованих блоків"
                value={decryptResult.blocks_decrypted}
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
    </div>
  );
}