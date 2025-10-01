import React from "react";
import { useNavigate } from "react-router-dom";

const PROJECT_TITLE = "MFA Auth Portal";
const PROJECT_DESC = "Welcome! Secure your account with Multi-Factor Authentication.";

const Startup: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">{PROJECT_TITLE}</h1>
        <p className="subtitle">{PROJECT_DESC}</p>
        <img
          src="/mfa.svg"
          alt="Logo"
          style={{ width: "80px", margin: "1em auto" }}
        />
        <button
          className="primary-btn"
          style={{ marginTop: "1.5em" }}
          onClick={() => navigate("/register")}
        >
          Get Started
        </button>
        <p style={{ marginTop: "1em", fontSize: "0.95em", color: "#aaa" }}>
          New here? <a href="/register" style={{ color: "#646cff" }}>Create an account</a>
        </p>
      </div>
    </div>
  );
};

export default Startup;