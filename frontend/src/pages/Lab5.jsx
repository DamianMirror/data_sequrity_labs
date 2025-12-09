import React, { useState } from "react";
import {
  generateDSAKeys,
  signString,
  verifyString,
  signFile,
  verifyFileSignature
} from "../api/backend.js";
import ResultCard from "../components/ResultCard.jsx";

export default function Lab5() {
  const [activeTab, setActiveTab] = useState("keys"); // keys, signString, verifyString, signFile, verifyFile
  const [keySize, setKeySize] = useState(2048);
  const [keys, setKeys] = useState(null);
  const [publicKeyInput, setPublicKeyInput] = useState("");
  const [privateKeyInput, setPrivateKeyInput] = useState("");

  // String signing state
  const [messageToSign, setMessageToSign] = useState("");
  const [signStringResult, setSignStringResult] = useState(null);

  // String verification state
  const [messageToVerify, setMessageToVerify] = useState("");
  const [signatureToVerify, setSignatureToVerify] = useState("");
  const [verifyStringResult, setVerifyStringResult] = useState(null);

  // File signing state
  const [fileToSign, setFileToSign] = useState(null);
  const [signFileResult, setSignFileResult] = useState(null);

  // File verification state
  const [fileToVerify, setFileToVerify] = useState(null);
  const [signatureFile, setSignatureFile] = useState(null);
  const [verifyFileResult, setVerifyFileResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const handleGenerateKeys = async () => {
    setLoading(true);
    try {
      const result = await generateDSAKeys(keySize);
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

  const handleSignString = async () => {
    if (!messageToSign.trim()) {
      alert("Введіть повідомлення для підпису!");
      return;
    }
    if (!privateKeyInput.trim()) {
      alert("Згенеруйте або введіть приватний ключ!");
      return;
    }

    setLoading(true);
    try {
      const result = await signString(messageToSign, privateKeyInput);
      if (result.success) {
        setSignStringResult(result);
        setSignatureToVerify(result.signature_hex);
        setMessageToVerify(messageToSign);
      } else {
        alert("Помилка при підписі: " + result.error);
      }
    } catch (error) {
      alert("Помилка при підписі: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyString = async () => {
    if (!messageToVerify.trim()) {
      alert("Введіть повідомлення для перевірки!");
      return;
    }
    if (!signatureToVerify.trim()) {
      alert("Введіть підпис для перевірки!");
      return;
    }
    if (!publicKeyInput.trim()) {
      alert("Згенеруйте або введіть публічний ключ!");
      return;
    }

    setLoading(true);
    try {
      const result = await verifyString(messageToVerify, signatureToVerify, publicKeyInput);
      if (result.success) {
        setVerifyStringResult(result);
      } else {
        alert("Помилка при перевірці: " + result.error);
      }
    } catch (error) {
      alert("Помилка при перевірці: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSignFile = async () => {
    if (!fileToSign) {
      alert("Оберіть файл для підпису!");
      return;
    }
    if (!privateKeyInput.trim()) {
      alert("Згенеруйте або введіть приватний ключ!");
      return;
    }

    setLoading(true);
    try {
      const result = await signFile(fileToSign, privateKeyInput);
      if (result.success) {
        setSignFileResult(result);
        // Save signature to file
        await downloadSignature(result.signature_hex, result.filename + '.sig');
      } else {
        alert("Помилка при підписі файлу: " + result.error);
      }
    } catch (error) {
      alert("Помилка при підписі файлу: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyFile = async () => {
    if (!fileToVerify) {
      alert("Оберіть файл для перевірки!");
      return;
    }
    if (!signatureFile) {
      alert("Оберіть файл підпису!");
      return;
    }
    if (!publicKeyInput.trim()) {
      alert("Згенеруйте або введіть публічний ключ!");
      return;
    }

    setLoading(true);
    try {
      const result = await verifyFileSignature(fileToVerify, signatureFile, publicKeyInput);
      if (result.success) {
        setVerifyFileResult(result);
      } else {
        alert("Помилка при перевірці підпису файлу: " + result.error);
      }
    } catch (error) {
      alert("Помилка при перевірці підпису файлу: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadSignature = async (signatureHex, filename) => {
    const blob = new Blob([signatureHex], { type: 'text/plain;charset=utf-8' });

    if (window.showSaveFilePicker) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: filename,
          types: [{
            description: 'Signature Files',
            accept: { 'text/plain': ['.sig'] },
          }],
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        alert('Підпис успішно збережено!');
        return;
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Error saving file:', err);
        }
        return;
      }
    }

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadKeys = async (keyType) => {
    if (!keys) return;

    const keyData = keyType === 'private' ? keys.private_key_pem : keys.public_key_pem;
    const blob = new Blob([keyData], { type: "text/plain;charset=utf-8" });
    const filename = `dsa_${keyType}_key_${keys.key_size}.pem`;

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

  return (
    <div className="page-container">
      <h2>Лабораторна №5 — Digital Signature Standard (DSS)</h2>

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
          onClick={() => setActiveTab("signString")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "signString" ? "#007bff" : "#f0f0f0",
            color: activeTab === "signString" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "signString" ? "bold" : "normal"
          }}
        >
          Підпис рядка
        </button>
        <button
          onClick={() => setActiveTab("verifyString")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "verifyString" ? "#007bff" : "#f0f0f0",
            color: activeTab === "verifyString" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "verifyString" ? "bold" : "normal"
          }}
        >
          Перевірка підпису рядка
        </button>
        <button
          onClick={() => setActiveTab("signFile")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "signFile" ? "#007bff" : "#f0f0f0",
            color: activeTab === "signFile" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "signFile" ? "bold" : "normal"
          }}
        >
          Підпис файлу
        </button>
        <button
          onClick={() => setActiveTab("verifyFile")}
          style={{
            padding: "10px 20px",
            backgroundColor: activeTab === "verifyFile" ? "#007bff" : "#f0f0f0",
            color: activeTab === "verifyFile" ? "white" : "black",
            border: "none",
            borderRadius: "4px 4px 0 0",
            cursor: "pointer",
            fontWeight: activeTab === "verifyFile" ? "bold" : "normal"
          }}
        >
          Перевірка підпису файлу
        </button>
      </div>

      {/* Key Generation Tab */}
      {activeTab === "keys" && (
        <div>
          <div className="form-container">
            <h3>Генерація DSA ключів</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Згенерируйте пару DSA ключів (приватний та публічний) для створення цифрових підписів.
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
                <option value={3072}>3072 біт (дуже безпечний, повільний)</option>
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
              {keys.key_info && (
                <>
                  <ResultCard
                    title="P bits"
                    value={`${keys.key_info.p_bits} біт`}
                  />
                  <ResultCard
                    title="Q bits"
                    value={`${keys.key_info.q_bits} біт`}
                  />
                  <ResultCard
                    title="G bits"
                    value={`${keys.key_info.g_bits} біт`}
                  />
                </>
              )}
              <div style={{ marginTop: "15px", padding: "15px", borderRadius: "8px", backgroundColor: "#f8f9fa", border: "1px solid #dee2e6" }}>
                <h4 style={{ marginTop: 0 }}>Публічний ключ (для перевірки підпису):</h4>
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
                <h4 style={{ marginTop: 0 }}>Приватний ключ (для створення підпису):</h4>
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
                  ⚠️ Зберігайте приватний ключ у безпечному місці! Без нього ви не зможете створювати підписи.
                </p>
              </div>
            </>
          )}
        </div>
      )}

      {/* Sign String Tab */}
      {activeTab === "signString" && (
        <div>
          <div className="form-container">
            <h3>Підпис рядка</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Створіть цифровий підпис для текстового повідомлення використовуючи DSA алгоритм.
            </p>
            <div style={{ marginBottom: "15px" }}>
              <label>Повідомлення для підпису:</label>
              <textarea
                value={messageToSign}
                onChange={(e) => setMessageToSign(e.target.value)}
                placeholder="Введіть текст для підпису..."
                style={{
                  width: "100%",
                  height: "100px",
                  padding: "10px",
                  marginTop: "5px",
                  fontSize: "14px",
                  resize: "vertical"
                }}
              />
            </div>
            <div style={{ marginBottom: "15px" }}>
              <label>Приватний ключ DSA (PEM формат):</label>
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
              onClick={handleSignString}
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
              {loading ? "Підписуємо..." : "Підписати повідомлення"}
            </button>
          </div>

          {signStringResult && signStringResult.success && (
            <>
              <ResultCard
                title="Повідомлення"
                value={signStringResult.message}
              />
              <ResultCard
                title="Довжина підпису"
                value={`${signStringResult.signature_length} байт`}
              />
              <div style={{ marginTop: "15px", padding: "15px", borderRadius: "8px", backgroundColor: "#f8f9fa", border: "1px solid #dee2e6" }}>
                <h4 style={{ marginTop: 0 }}>Підпис (HEX формат):</h4>
                <textarea
                  value={signStringResult.signature_hex}
                  readOnly
                  style={{
                    width: "100%",
                    height: "80px",
                    fontFamily: "monospace",
                    fontSize: "11px",
                    padding: "10px",
                    resize: "vertical",
                    wordBreak: "break-all"
                  }}
                />
                <button
                  onClick={() => downloadSignature(signStringResult.signature_hex, 'signature.txt')}
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
                  Зберегти підпис
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Verify String Tab */}
      {activeTab === "verifyString" && (
        <div>
          <div className="form-container">
            <h3>Перевірка підпису рядка</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Перевірте автентичність цифрового підпису текстового повідомлення.
            </p>
            <div style={{ marginBottom: "15px" }}>
              <label>Повідомлення:</label>
              <textarea
                value={messageToVerify}
                onChange={(e) => setMessageToVerify(e.target.value)}
                placeholder="Введіть текст для перевірки..."
                style={{
                  width: "100%",
                  height: "100px",
                  padding: "10px",
                  marginTop: "5px",
                  fontSize: "14px",
                  resize: "vertical"
                }}
              />
            </div>
            <div style={{ marginBottom: "15px" }}>
              <label>Підпис (HEX формат):</label>
              <textarea
                value={signatureToVerify}
                onChange={(e) => setSignatureToVerify(e.target.value)}
                placeholder="Вставте підпис у шістнадцятковому форматі..."
                style={{
                  width: "100%",
                  height: "80px",
                  fontFamily: "monospace",
                  fontSize: "11px",
                  padding: "10px",
                  marginTop: "5px",
                  resize: "vertical"
                }}
              />
            </div>
            <div style={{ marginBottom: "15px" }}>
              <label>Публічний ключ DSA (PEM формат):</label>
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
              onClick={handleVerifyString}
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
              {loading ? "Перевіряємо..." : "Перевірити підпис"}
            </button>
          </div>

          {verifyStringResult && verifyStringResult.success && (
            <>
              <div
                style={{
                  padding: "15px",
                  borderRadius: "8px",
                  backgroundColor: verifyStringResult.is_valid ? "#d4edda" : "#f8d7da",
                  border: verifyStringResult.is_valid ? "2px solid #28a745" : "2px solid #dc3545",
                  marginTop: "15px"
                }}
              >
                <h3 style={{ margin: "0 0 10px 0", color: verifyStringResult.is_valid ? "#155724" : "#721c24" }}>
                  {verifyStringResult.is_valid ? "✓ Підпис дійсний!" : "✗ Підпис недійсний!"}
                </h3>
                <p style={{ margin: 0, color: verifyStringResult.is_valid ? "#155724" : "#721c24" }}>
                  {verifyStringResult.verification_message}
                </p>
              </div>
              <ResultCard
                title="Повідомлення"
                value={verifyStringResult.message}
              />
            </>
          )}
        </div>
      )}

      {/* Sign File Tab */}
      {activeTab === "signFile" && (
        <div>
          <div className="form-container">
            <h3>Підпис файлу</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Створіть цифровий підпис для файлу. Підпис буде збережено у форматі .sig.
            </p>
            <div style={{ marginBottom: "15px" }}>
              <label>Виберіть файл для підпису:</label>
              <input
                type="file"
                onChange={(e) => setFileToSign(e.target.files[0])}
                style={{ marginTop: "10px", display: "block" }}
              />
              {fileToSign && (
                <div style={{ marginTop: "10px", color: "#666", fontSize: "14px" }}>
                  Обраний файл: <strong>{fileToSign.name}</strong> ({(fileToSign.size / 1024).toFixed(2)} KB)
                </div>
              )}
            </div>
            <div style={{ marginBottom: "15px" }}>
              <label>Приватний ключ DSA (PEM формат):</label>
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
              onClick={handleSignFile}
              disabled={loading || !fileToSign}
              style={{
                padding: "10px 20px",
                fontSize: "16px",
                backgroundColor: "#28a745",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: loading || !fileToSign ? "not-allowed" : "pointer"
              }}
            >
              {loading ? "Підписуємо..." : "Підписати файл"}
            </button>
          </div>

          {signFileResult && signFileResult.success && (
            <>
              <ResultCard
                title="Ім'я файлу"
                value={signFileResult.filename}
              />
              <ResultCard
                title="Розмір файлу"
                value={`${signFileResult.file_size} bytes`}
              />
              <ResultCard
                title="Довжина підпису"
                value={`${signFileResult.signature_length} байт`}
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
                  ✓ Файл успішно підписано
                </h3>
                <p style={{ margin: 0, color: "#155724" }}>
                  Файл підпису (.sig) автоматично завантажено
                </p>
              </div>
              <div style={{ marginTop: "15px", padding: "15px", borderRadius: "8px", backgroundColor: "#f8f9fa", border: "1px solid #dee2e6" }}>
                <h4 style={{ marginTop: 0 }}>Підпис (HEX формат):</h4>
                <textarea
                  value={signFileResult.signature_hex}
                  readOnly
                  style={{
                    width: "100%",
                    height: "80px",
                    fontFamily: "monospace",
                    fontSize: "11px",
                    padding: "10px",
                    resize: "vertical",
                    wordBreak: "break-all"
                  }}
                />
              </div>
            </>
          )}
        </div>
      )}

      {/* Verify File Tab */}
      {activeTab === "verifyFile" && (
        <div>
          <div className="form-container">
            <h3>Перевірка підпису файлу</h3>
            <p style={{ color: "#666", marginBottom: "15px" }}>
              Перевірте автентичність та цілісність файлу за допомогою цифрового підпису.
            </p>
            <div style={{ marginBottom: "15px" }}>
              <label>Виберіть файл для перевірки:</label>
              <input
                type="file"
                onChange={(e) => setFileToVerify(e.target.files[0])}
                style={{ marginTop: "10px", display: "block" }}
              />
              {fileToVerify && (
                <div style={{ marginTop: "10px", color: "#666", fontSize: "14px" }}>
                  Обраний файл: <strong>{fileToVerify.name}</strong> ({(fileToVerify.size / 1024).toFixed(2)} KB)
                </div>
              )}
            </div>
            <div style={{ marginBottom: "15px" }}>
              <label>Виберіть файл підпису (.sig):</label>
              <input
                type="file"
                onChange={(e) => setSignatureFile(e.target.files[0])}
                style={{ marginTop: "10px", display: "block" }}
              />
              {signatureFile && (
                <div style={{ marginTop: "10px", color: "#666", fontSize: "14px" }}>
                  Обраний файл підпису: <strong>{signatureFile.name}</strong>
                </div>
              )}
            </div>
            <div style={{ marginBottom: "15px" }}>
              <label>Публічний ключ DSA (PEM формат):</label>
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
              onClick={handleVerifyFile}
              disabled={loading || !fileToVerify || !signatureFile}
              style={{
                padding: "10px 20px",
                fontSize: "16px",
                backgroundColor: "#28a745",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: loading || !fileToVerify || !signatureFile ? "not-allowed" : "pointer"
              }}
            >
              {loading ? "Перевіряємо..." : "Перевірити підпис файлу"}
            </button>
          </div>

          {verifyFileResult && verifyFileResult.success && (
            <>
              <div
                style={{
                  padding: "15px",
                  borderRadius: "8px",
                  backgroundColor: verifyFileResult.is_valid ? "#d4edda" : "#f8d7da",
                  border: verifyFileResult.is_valid ? "2px solid #28a745" : "2px solid #dc3545",
                  marginTop: "15px"
                }}
              >
                <h3 style={{ margin: "0 0 10px 0", color: verifyFileResult.is_valid ? "#155724" : "#721c24" }}>
                  {verifyFileResult.is_valid ? "✓ Підпис файлу дійсний!" : "✗ Підпис файлу недійсний!"}
                </h3>
                <p style={{ margin: 0, color: verifyFileResult.is_valid ? "#155724" : "#721c24" }}>
                  {verifyFileResult.verification_message}
                </p>
              </div>
              <ResultCard
                title="Ім'я файлу"
                value={verifyFileResult.filename}
              />
              <ResultCard
                title="Файл підпису"
                value={verifyFileResult.signature_filename}
              />
              <ResultCard
                title="Розмір файлу"
                value={`${verifyFileResult.file_size} bytes`}
              />
            </>
          )}
        </div>
      )}
    </div>
  );
}