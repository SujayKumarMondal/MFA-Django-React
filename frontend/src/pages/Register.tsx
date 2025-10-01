import React, { useState } from "react";
import { registerUser } from "../api/api";
import { useNavigate } from "react-router-dom";

const PROJECT_TITLE = "MFA Auth Portal";
const PROJECT_DESC = "Secure your account with Multi-Factor Authentication.";

const Register: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await registerUser({ email, password });
      alert("Registered successfully!");
      navigate("/login");
    } catch (err: any) {
      if (err.response && err.response.data && err.response.data.error === "User already registered") {
        alert("User already registered");
      } else {
        alert("Error registering user");
      }
    }
  };

  return (
    <div className="container">
      <form className="card form" onSubmit={handleSubmit}>
        <h1 className="title">{PROJECT_TITLE}</h1>
        <p className="subtitle">{PROJECT_DESC}</p>
        <h2 style={{ marginBottom: "0.5em" }}>Register</h2>
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
        <button className="primary-btn" type="submit">Register</button>
        <p style={{ marginTop: "1em", fontSize: "0.95em", color: "#aaa" }}>
          Already have an account? <a href="/login" style={{ color: "#646cff" }}>Login</a>
        </p>
      </form>
    </div>
  );
};

export default Register;