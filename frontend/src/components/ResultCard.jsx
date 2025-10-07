import React from "react";

export default function ResultCard({ title, value }) {
  return (
    <div className="result-card">
      <h3>{title}</h3>
      <p>{value}</p>
    </div>
  );
}
