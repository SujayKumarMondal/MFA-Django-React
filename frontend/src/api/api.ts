import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8015/auth",
  withCredentials: true // for httpOnly cookies if needed
});

export const registerUser = (data: { email: string; password: string }) => api.post("/register/", data);
export const loginUser = (data: { email: string; password: string }) => api.post("/login/", data);
export const setupMFA = () => api.get("/mfa/setup/");
export const verifyMFA = (data: { token: string }) => api.post("/mfa/verify/", data);
export const sendOTP = () => api.post("/mfa/send-otp/");
export const refreshToken = (data: { refresh: string }) => api.post("/token/refresh/", data);
export const logoutUser = () => api.post("/logout/");

export default api;
