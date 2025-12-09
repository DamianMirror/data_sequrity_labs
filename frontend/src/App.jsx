import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Lab1 from "./pages/Lab1.jsx";
import Lab2 from "./pages/Lab2.jsx";
import Lab3 from "./pages/Lab3.jsx";
import Lab4 from "./pages/Lab4.jsx";
import Lab5 from "./pages/Lab5.jsx";

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
        <Route path="/lab3" element={<Lab3 />} />
        <Route path="/lab4" element={<Lab4 />} />
        <Route path="/lab5" element={<Lab5 />} />
      </Routes>
    </BrowserRouter>
  );
}
