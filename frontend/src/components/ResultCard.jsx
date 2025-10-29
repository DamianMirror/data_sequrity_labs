import React, { useState } from "react";

export default function ResultCard({ title, value, collapsible = false, displayPercentage = 100, onPercentageChange }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (collapsible) {
    const numbers = value.split(", ");
    const percentToShow = Math.min(100, Math.max(0, displayPercentage));
    const numbersToShow = Math.ceil((numbers.length * percentToShow) / 100);
    const previewNumbers = numbers.slice(0, numbersToShow);
    const displayValue = isExpanded ? value : previewNumbers.join(", ");
    const hasMore = numbers.length > numbersToShow;

    return (
      <div className="result-card">
        <h3 style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
          <span>{title}</span>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            {onPercentageChange && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <label style={{ fontSize: '12px', margin: 0 }}>Показати:</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={displayPercentage}
                  onChange={(e) => onPercentageChange(parseInt(e.target.value) || 0)}
                  style={{
                    width: '60px',
                    padding: '4px',
                    fontSize: '12px',
                    borderRadius: '4px',
                    border: '1px solid #ccc'
                  }}
                />
                <span style={{ fontSize: '12px' }}>%</span>
              </div>
            )}
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
          </div>
        </h3>
        <p style={{ wordBreak: 'break-word' }}>
          {displayValue}
          {!isExpanded && numbersToShow < numbers.length && (
            <span style={{ color: '#888', fontStyle: 'italic' }}>
              {' '}... (показано {numbersToShow} з {numbers.length})
            </span>
          )}
        </p>
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
