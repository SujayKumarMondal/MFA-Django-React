import React, { useEffect, useState } from "react";
import { setupMFA } from "../api/api";
import { useNavigate } from "react-router-dom";

const PROJECT_TITLE = "MFA Auth Portal";
const PROJECT_DESC = "Secure your account with Multi-Factor Authentication.";

const MFASetup: React.FC = () => {
  const [qrCode, setQrCode] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchQR = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await setupMFA();

        // ✅ Your backend returns: { "mfa_secret": "...", "qr": "data:image/png;base64,..." }
        // so use "qr" not "qr_code"
        if (res.data.qr) {
          setQrCode(res.data.qr);
        } else {
          throw new Error("QR data not found in response");
        }
      } catch (err: any) {
        console.error("MFA setup error:", err);
        setError("Failed to setup MFA. Please login again or check server.");
      } finally {
        setLoading(false);
      }
    };

    fetchQR();
  }, []);

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <h1 className="title">{PROJECT_TITLE}</h1>
          <p className="subtitle">Loading MFA setup...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="card">
          <h1 className="title">{PROJECT_TITLE}</h1>
          <p className="subtitle" style={{ color: "red" }}>
            {error}
          </p>
          <button className="primary-btn" onClick={() => navigate("/login")}>
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">{PROJECT_TITLE}</h1>
        <p className="subtitle">{PROJECT_DESC}</p>

        <h2 style={{ marginBottom: "0.5em" }}>Setup MFA</h2>
        <p className="subtitle">
          Scan the QR code below with your authenticator app (e.g., Google Authenticator or Authy).
        </p>

        {qrCode ? (
          <img
            className="qr-img"
            src={qrCode}
            alt="MFA QR Code"
            style={{ width: "200px", marginTop: "1em" }}
          />
        ) : (
          <p>No QR code available.</p>
        )}

        <button
          className="primary-btn"
          style={{ marginTop: "1em" }}
          onClick={() => navigate("/mfa-verify")}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default MFASetup;
