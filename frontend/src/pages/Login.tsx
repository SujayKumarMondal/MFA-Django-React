import React, { useState } from "react";
import { loginUser } from "../api/api";
import { useNavigate } from "react-router-dom";

const PROJECT_TITLE = "MFA Auth Portal";
const PROJECT_DESC = "Secure your account with Multi-Factor Authentication.";

const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await loginUser({ email, password });
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      navigate("/mfa-setup");
    } catch (err) {
      alert("Invalid credentials");
    }
  };

  return (
    <div className="container">
      <form className="card form" onSubmit={handleSubmit}>
        <h1 className="title">{PROJECT_TITLE}</h1>
        <p className="subtitle">{PROJECT_DESC}</p>
        <h2 style={{ marginBottom: "0.5em" }}>Login</h2>
        <input
          className="input"
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          className="input"
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button className="primary-btn" type="submit">Login</button>
        <p style={{ marginTop: "1em", fontSize: "0.95em", color: "#aaa" }}>
          Don't have an account? <a href="/register" style={{ color: "#646cff" }}>Register</a>
        </p>
      </form>
    </div>
  );
};

export default Login;