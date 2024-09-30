import { createContext, useContext, useEffect, useState } from "react";

import {
  registerRequest,
  loginRequest,
  logoutRequest,
  checkAuthRequest
} from "../api/auth";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [errors, setErrors] = useState(null);

  const signup = async (user) => {
    try {
      const res = await registerRequest(user);
      setUser(res);
      setIsAuthenticated(true);
      setLoading(false);
    } catch (error) {
      setErrors(error.response.data);
      setLoading(false);
    }
  };

  const signin = async (user) => {
    try {
      const res = await loginRequest(user);
      setUser(res);
      setIsAuthenticated(true);
      setLoading(false);
    } catch (error) {
      setErrors(error.response.data);
      setLoading(false);
    }
  };

  const logout = async () => {
    await logoutRequest();
    setUser(null);
    setIsAuthenticated(false);
    setLoading(false);
  };

  useEffect(() => {
    const checkLogin = async () => {
      try {
        const res = await checkAuthRequest();
        if (res) {
          setUser(res);
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
        }
      } catch (error) {
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };
    checkLogin();
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated, loading, errors, signup, signin, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
};


export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
