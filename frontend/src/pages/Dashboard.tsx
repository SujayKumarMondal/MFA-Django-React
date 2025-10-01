import React from "react";
import { logoutUser } from "../api/api";
import { useNavigate } from "react-router-dom";

const PROJECT_TITLE = "MFA Auth Portal";
const PROJECT_DESC = "Secure your account with Multi-Factor Authentication.";

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logoutUser();
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/");
  };

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">{PROJECT_TITLE}</h1>
        <p className="subtitle">{PROJECT_DESC}</p>
        <h2 style={{ marginBottom: "0.5em" }}>Dashboard</h2>
        <p className="subtitle">Welcome! You are logged in.</p>
        <button className="primary-btn" onClick={handleLogout}>Logout</button>
      </div>
    </div>
  );
};

export default Dashboard;