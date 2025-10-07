import React, { useState } from "react";

export default function ResultCard({ title, value, collapsible = false }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (collapsible) {
    const numbers = value.split(", ");
    const previewNumbers = numbers.slice(0, 8); // Показуємо перші 8 чисел
    const displayValue = isExpanded ? value : previewNumbers.join(", ");
    const hasMore = numbers.length > 8;

    return (
      <div className="result-card">
        <h3 style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {title}
          {hasMore && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              style={{
                background: 'none',
                border: '1px solid #5a67d8',
                color: '#5a67d8',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '12px',
                cursor: 'pointer'
              }}
            >
              {isExpanded ? 'Згорнути ▲' : `Показати всі (${numbers.length}) ▼`}
            </button>
          )}
        </h3>
        <p>{displayValue}</p>
      </div>
    );
  }

  return (
    <div className="result-card">
      <h3>{title}</h3>
      <p>{value}</p>
    </div>
  );
}
