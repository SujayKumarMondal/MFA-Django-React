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
      console.log("Access token:", res.data.access);
      localStorage.setItem("access_token", res.data.access);
      sessionStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      sessionStorage.setItem("refresh_token", res.data.refresh);
      navigate("/mfa-setup");
    } catch (err) {
      alert("Invalid credentials");
    }
  };

  // Forgot password (modal) state & handler — will send an email with reset link
  const [showReset, setShowReset] = useState(false);
  const [resetEmail, setResetEmail] = useState("");

  const handleResetRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const api = await import("../api/api");
      await api.requestPasswordReset({ email: resetEmail });
      alert("If an account with that email exists, a reset link has been sent.");
      setShowReset(false);
      setResetEmail("");
    } catch (err: any) {
      const msg = err?.response?.data?.error || err?.response?.data || err?.message || "Failed to request password reset";
      alert(msg);
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

        <p style={{ marginTop: "0.5em", fontSize: "0.95em" }}>
          <a href="#" onClick={(e) => { e.preventDefault(); setShowReset(!showReset); }} style={{ color: "#ff6b6b" }}>
            {showReset ? "Cancel password reset" : "Forgot password?"}
          </a>
        </p>

        {showReset && (
          <div style={{ position: "fixed", left: 0, top: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.4)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div className="card form" style={{ width: 360, padding: "1.25em" }}>
              <h3 style={{ marginTop: 0 }}>Reset Password</h3>
              <p style={{ color: "#666", fontSize: "0.95em" }}>Enter your email and we'll send a secure reset link.</p>
              <form onSubmit={handleResetRequest}>
                <input
                  className="input"
                  type="email"
                  placeholder="Email"
                  value={resetEmail}
                  onChange={e => setResetEmail(e.target.value)}
                  required
                />
                <div style={{ display: "flex", gap: "0.5em", marginTop: "0.5em" }}>
                  <button className="primary-btn" type="submit" style={{ flex: 1 }}>Send reset link</button>
                  <button className="secondary-btn" onClick={(e) => { e.preventDefault(); setShowReset(false); }} style={{ flex: 0.6 }}>Cancel</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default Login;