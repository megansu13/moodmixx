import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import "semantic-ui-css/semantic.min.css";
import Advanced from "./Advanced";
import "./App.css";
import Login from "./Login";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate replace to="/login" />} />
      <Route path="/login" element={<Login />} />
      <Route path="/content" element={<Advanced />} />
    </Routes>
  );
}

export default App;
