import { Navigate } from "react-router-dom";
import React from "react";

interface Props {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<Props> = ({ children }) => {
  const token = localStorage.getItem("access_token");
  if (!token) return <Navigate to="/login" />;
  return <>{children}</>;
};

export default ProtectedRoute;
