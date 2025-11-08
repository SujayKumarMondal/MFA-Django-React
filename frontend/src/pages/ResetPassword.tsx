import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const uid = searchParams.get("uid") || "";
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");

  useEffect(() => {
    if (!uid || !token) {
      // if missing params, redirect to login
      navigate("/login");
    }
  }, [uid, token, navigate]);

  const handleConfirm = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== password2) {
      alert("Passwords do not match");
      return;
    }
    try {
      const api = await import("../api/api");
      await api.confirmPasswordReset({ uid, token, password, password2 });
      alert("Password has been reset. You can now login.");
      navigate("/login");
    } catch (err: any) {
      const msg = err?.response?.data?.error || err?.response?.data || err?.message || "Failed to reset password";
      alert(msg);
    }
  };

  return (
    <div className="container">
      <div className="card form">
        <h2>Set a new password</h2>
        <p style={{ color: "#666" }}>Choose a strong password for your account.</p>
        <form onSubmit={handleConfirm}>
          <input className="input" type="password" placeholder="New password" value={password} onChange={e => setPassword(e.target.value)} required />
          <input className="input" type="password" placeholder="Confirm new password" value={password2} onChange={e => setPassword2(e.target.value)} required />
          <button className="primary-btn" type="submit">Save password</button>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
