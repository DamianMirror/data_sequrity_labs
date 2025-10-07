import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Lab1 from "./pages/Lab1.jsx";
import Lab2 from "./pages/Lab2.jsx";

function Home() {
  return (
    <div className="page-container" style={{ textAlign: 'center' }}>
      <h1>Sequrity Labs</h1>
      <p>Оберіть лабораторну роботу з навігаційного меню</p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/lab1" element={<Lab1 />} />
        <Route path="/lab2" element={<Lab2 />} />
      </Routes>
    </BrowserRouter>
  );
}
