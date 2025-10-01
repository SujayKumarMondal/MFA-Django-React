import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Register from "./pages/Register";
import Login from "./pages/Login";
import MFASetup from "./pages/MFASetup";
import MFAVerify from "./pages/MFAVerify";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";
import Startup from "./pages/Startup";

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Startup />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/mfa-setup" element={<ProtectedRoute><MFASetup /></ProtectedRoute>} />
        <Route path="/mfa-verify" element={<ProtectedRoute><MFAVerify /></ProtectedRoute>} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
