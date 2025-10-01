import React, { useState } from "react";
import { verifyMFA } from "../api/api";
// import { sendOTP } from "../api/api";
import { useNavigate } from "react-router-dom";

const PROJECT_TITLE = "MFA Auth Portal";
const PROJECT_DESC = "Secure your account with Multi-Factor Authentication.";

const MFAVerify: React.FC = () => {
  const [token, setToken] = useState("");
  const navigate = useNavigate();

  const handleVerify = async () => {
    try {
      await verifyMFA({ token });
      alert("MFA verified!");
      navigate("/dashboard");
    } catch (err) {
      alert("Invalid MFA token");
    }
  };

  // const handleSendOTP = async () => {
  //   try {
  //     await sendOTP();
  //     alert("OTP sent to your email");
  //   } catch {
  //     alert("Failed to send OTP");
  //   }
  // };

  return (
    <div className="container">
      <div className="card form">
        <h1 className="title">{PROJECT_TITLE}</h1>
        <p className="subtitle">{PROJECT_DESC}</p>
        <h2 style={{ marginBottom: "0.5em" }}>Verify MFA</h2>
        <input
          className="input"
          type="text"
          placeholder="Enter TOTP or OTP"
          value={token}
          onChange={e => setToken(e.target.value)}
          required
        />
        <button className="primary-btn" onClick={handleVerify}>Verify</button>
        {/* <button className="secondary-btn" onClick={handleSendOTP}>Send OTP</button> */}
        <p style={{ marginTop: "1em", fontSize: "0.95em", color: "#aaa" }}>
          Need help? Check your email for the OTP or contact support.
        </p>
      </div>
    </div>
  );
};

export default MFAVerify;