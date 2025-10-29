import React, { useState } from "react";
import { generateNumbers } from "../api/backend.js";
import ResultCard from "../components/ResultCard.jsx";

export default function Lab1() {
  const [data, setData] = useState(null);
  const [displayPercentage, setDisplayPercentage] = useState(100);
  const [params, setParams] = useState({
    mPower: 20,    // Степінь двійки для модуля (2^mPower - 1)
    a: 343,         // Множник
    c: 89,         // Приріст
    x0: 1,         // Початкове значення
    n: 20          // Кількість чисел
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setParams(prev => ({
      ...prev,
      [name]: parseInt(value) || 0
    }));
  };

  const handleGenerate = async () => {
    // Перетворюємо mPower в m (2^mPower - 1)
    const apiParams = {
      ...params,
      m: Math.pow(2, params.mPower) - 1
    };
    delete apiParams.mPower; // Видаляємо mPower з параметрів для API

    const result = await generateNumbers(apiParams);
    console.log('API Response:', result); // Додаємо для дебагу
    setData(result);
  };

  const getPowerFromM = (m) => {
    if (m <= 0) return 0;
    let power = 1;
    while (Math.pow(2, power) - 1 < m) {
      power++;
    }
    if (Math.pow(2, power) - 1 === m) {
      return power;
    } else {
      return Math.abs(Math.pow(2, power - 1) - 1 - m) < Math.abs(Math.pow(2, power) - 1 - m) ? power - 1 : power;
    }
  };

  const calculatePiEstimate = (coprimePercent) => {
    if (coprimePercent <= 0) return 0;
    return Math.sqrt(6 / coprimePercent);
  };

  const generateCSV = () => {
    if (!data) return;

    const m = Math.pow(2, params.mPower) - 1;
    const csvRows = [];

    // Додаємо BOM для правильного відображення UTF-8 в Excel
    csvRows.push('\ufeff');

    // Заголовки
    csvRows.push('Type,Parameter,Value,Description');

    // Параметри
    csvRows.push(`Parameters,m (Модуль),${m},2^${params.mPower} - 1`);
    csvRows.push(`Parameters,a (Множник),${params.a},Параметр множника`);
    csvRows.push(`Parameters,c (Приріст),${params.c},Параметр приросту`);
    csvRows.push(`Parameters,x0 (Початкове значення),${params.x0},Seed для генератора`);
    csvRows.push(`Parameters,n (Кількість чисел),${params.n},Загальна кількість згенерованих чисел`);

    // Порожній рядок
    csvRows.push(',,,');

    // Результати
    const coprimePercent = data.cesaro_probability || 0;
    const relativeError = data.relative_error || 0;
    const piEstimate = calculatePiEstimate(coprimePercent);

    csvRows.push(`Results,Coprime Percentage,${coprimePercent.toFixed(6)},Відсоток взаємно простих пар: ${(coprimePercent * 100).toFixed(2)}%`);
    csvRows.push(`Results,Relative Error,${relativeError.toFixed(6)},Відносна похибка оцінки π: ${relativeError.toFixed(4)}%`);
    csvRows.push(`Results,Pi Estimate,${piEstimate.toFixed(6)},Оцінка π через тест Чезаро`);

    // Порожній рядок
    csvRows.push(',,,');

    // Згенеровані числа
    if (data.numbers && Array.isArray(data.numbers)) {
      data.numbers.forEach((number, index) => {
        csvRows.push(`Generated Numbers,Number ${index + 1},${number},x_${index + 1} = ${number}`);
      });
    }

    return csvRows.join('\n');
  };

  const handleDownloadCSV = () => {
    if (!data) {
      alert('Спершу згенеруйте послідовність!');
      return;
    }

    // Запитуємо назву файлу у користувача
    const timestamp = new Date().toISOString().replace(/[-:]/g, '').split('.')[0].replace('T', '_');
    const randomId = Math.random().toString(36).substring(2, 10);
    const defaultFilename = `lcg_results_${timestamp}_${randomId}`;

    const userFilename = prompt('Введіть назву файлу (без розширення .csv):', defaultFilename);

    // Якщо користувач натиснув Cancel або залишив порожнім
    if (!userFilename) {
      return;
    }

    const csvContent = generateCSV();
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');

    // Додаємо розширення .csv, якщо користувач його не вказав
    const filename = userFilename.endsWith('.csv') ? userFilename : `${userFilename}.csv`;

    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();

    // Очищаємо URL після завантаження
    URL.revokeObjectURL(link.href);
  };

  return (
    <div className="page-container">
      <h2>Лабораторна №1 — Генерація псевдовипадкових чисел (LCG)</h2>

      <div className="form-container">
        <h3>Параметри LCG</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px" }}>
          <div>
            <label>Степінь для модуля (2^x - 1):</label>
            <input
              type="number"
              name="mPower"
              value={params.mPower}
              onChange={handleInputChange}
              min="1"
              max="30"
              style={{ width: "100%", padding: "5px", marginTop: "5px" }}
            />
            <small style={{ color: "#666" }}>m = 2^{params.mPower} - 1 = {Math.pow(2, params.mPower) - 1}</small>
          </div>
          <div>
            <label>Множник (a):</label>
            <input
              type="number"
              name="a"
              value={params.a}
              onChange={handleInputChange}
              style={{ width: "100%", padding: "5px", marginTop: "5px" }}
            />
          </div>
          <div>
            <label>Приріст (c):</label>
            <input
              type="number"
              name="c"
              value={params.c}
              onChange={handleInputChange}
              style={{ width: "100%", padding: "5px", marginTop: "5px" }}
            />
          </div>
          <div>
            <label>Початкове значення (X₀):</label>
            <input
              type="number"
              name="x0"
              value={params.x0}
              onChange={handleInputChange}
              style={{ width: "100%", padding: "5px", marginTop: "5px" }}
            />
          </div>
          <div>
            <label>Кількість чисел (n):</label>
            <input
              type="number"
              name="n"
              value={params.n}
              onChange={handleInputChange}
              min="1"
              max="1000"
              style={{ width: "100%", padding: "5px", marginTop: "5px" }}
            />
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <button onClick={handleGenerate} style={{ padding: "10px 20px", fontSize: "16px" }}>
          Згенерувати послідовність
        </button>

        {data && (
          <button
            onClick={handleDownloadCSV}
            style={{
              padding: "10px 20px",
              fontSize: "16px",
              backgroundColor: "#28a745",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            📥 Скачати CSV
          </button>
        )}
      </div>

      {data && (
        <>
          <ResultCard
            title="Згенеровані числа"
            value={data.numbers?.join(", ") || "Немає даних"}
            collapsible={true}
            displayPercentage={displayPercentage}
            onPercentageChange={setDisplayPercentage}
          />
          <ResultCard
            title="Ймовірність взаємно простих чисел"
            value={data.cesaro_probability !== undefined ? `${(data.cesaro_probability * 100).toFixed(2)}%` : "Немає даних"}
          />
          <ResultCard
            title="Відносна похибка оцінки π"
            value={data.relative_error !== undefined ? `${data.relative_error.toFixed(4)}%` : "Немає даних"}
          />
        </>
      )}
    </div>
  );
}

