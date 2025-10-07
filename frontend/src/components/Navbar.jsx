import React from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav style={{ padding: "10px", background: "#f4f4f4" }}>
      <Link to="/" style={{ marginRight: "10px" }}>Головна</Link>
      <Link to="/lab1" style={{ marginRight: "10px" }}>Lab 1</Link>
      <Link to="/lab2">Lab 2</Link>
    </nav>
  );
}
