import axios from "axios";

// --- Base Configuration ---
const api = axios.create({
  baseURL: "http://localhost:8015/auth", // backend base URL
  withCredentials: false, // change to true only if backend uses cookies
  headers: {
    "Content-Type": "application/json",
  },
});

// --- Helper functions for token management ---
const getAccessToken = () => localStorage.getItem("access_token");
const getRefreshToken = () => localStorage.getItem("refresh_token");

const setAccessToken = (token: string) => {
  localStorage.setItem("access_token", token);
};

const clearTokens = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  sessionStorage.removeItem("access_token");
  sessionStorage.removeItem("refresh_token");
};

// --- Request Interceptor ---
// Automatically attach access token for all requests
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

// --- Response Interceptor ---
// Automatically refresh token if access token expired (401)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Only attempt refresh once per request
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refresh = getRefreshToken();
      if (refresh) {
        try {
          const res = await api.post("/token/refresh/", { refresh });
          const newAccess = res.data.access;

          setAccessToken(newAccess);

          // Retry original request with new access token
          originalRequest.headers["Authorization"] = `Bearer ${newAccess}`;
          return api(originalRequest);
        } catch (refreshErr) {
          clearTokens();
          window.location.href = "/login"; // redirect user to login page
        }
      } else {
        clearTokens();
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

// --- API Endpoints ---

export const registerUser = (data: { email: string; password: string }) =>
  api.post("/register/", data);

export const loginUser = async (data: { email: string; password: string }) => {
  const res = await api.post("/login/", data);

  // Save access & refresh tokens locally
  const { access, refresh } = res.data;
  if (access && refresh) {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
    sessionStorage.setItem("access_token", access);
    sessionStorage.setItem("refresh_token", refresh);
  }

  return res;
};

// MFA setup — get QR and secret
export const setupMFA = () => api.get("/mfa/setup/");

// Verify MFA code
export const verifyMFA = (data: { token: string }) => api.post("/mfa/verify/", data);

// Send OTP (email-based)
export const sendOTP = () => api.post("/mfa/send-otp/");

// Refresh token manually
export const refreshToken = (data: { refresh: string }) => api.post("/token/refresh/", data);

// Logout
export const logoutUser = async () => {
  try {
    await api.post("/logout/");
  } finally {
    clearTokens();
  }
};

// Password reset flow
export const requestPasswordReset = (data: { email: string }) =>
  api.post("/reset-password/request/", data);

export const confirmPasswordReset = (data: {
  uid: string;
  token: string;
  password: string;
  password2: string;
}) => api.post("/reset-password/confirm/", data);

export default api;
