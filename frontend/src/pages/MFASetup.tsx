import React, { useEffect, useState } from "react";
import { setupMFA } from "../api/api";
import { useNavigate } from "react-router-dom";

const PROJECT_TITLE = "MFA Auth Portal";
const PROJECT_DESC = "Secure your account with Multi-Factor Authentication.";

const MFASetup: React.FC = () => {
  const [qrCode, setQrCode] = useState<string>("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchQR = async () => {
      try {
        const res = await setupMFA();
        setQrCode(res.data.qr_code);
      } catch (err) {
        alert("Error setting up MFA");
      }
    };
    fetchQR();
  }, []);

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">{PROJECT_TITLE}</h1>
        <p className="subtitle">{PROJECT_DESC}</p>
        <h2 style={{ marginBottom: "0.5em" }}>Setup MFA</h2>
        <p className="subtitle">Scan the QR code below with your authenticator app.</p>
        {qrCode && <img className="qr-img" src={qrCode} alt="MFA QR Code" />}
        <button className="primary-btn" onClick={() => navigate("/mfa-verify")}>Next</button>
      </div>
    </div>
  );
};

export default MFASetup;