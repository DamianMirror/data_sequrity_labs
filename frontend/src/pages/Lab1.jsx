import React, { useState } from "react";
import { generateNumbers } from "../api/backend.js";
import ResultCard from "../components/ResultCard.jsx";

export default function Lab1() {
  const [data, setData] = useState(null);
  const [params, setParams] = useState({
    mPower: 20,    // Степінь двійки для модуля (2^mPower - 1)
    a: 73,         // Множник
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

      <button onClick={handleGenerate} style={{ padding: "10px 20px", fontSize: "16px" }}>
        Згенерувати послідовність
      </button>

      {data && (
        <>
          <ResultCard title="Згенеровані числа" value={data.numbers?.join(", ") || "Немає даних"} />
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

