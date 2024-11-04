import { createContext, useContext, useEffect, useState } from "react";
import {
  registerRequest,
  loginRequest,
  logoutRequest,
  checkAuthRequest
} from "../api/auth";
import Cookies from 'js-cookie';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [errors, setErrors] = useState(null);

  const signup = async (user) => {
    setLoading(true);
    try {
      const res = await registerRequest(user);
      setUser(res);
      setIsAuthenticated(true);
    } catch (error) {
      setErrors(error.response.data);
    } finally {
      setLoading(false);
    }
  };

  const signin = async (user) => {
    setLoading(true);
    try {
      const res = await loginRequest(user);
      setUser(res);
      setIsAuthenticated(true);
      Cookies.set('access_token', res.token, { expires: 1 });
      return true;
    } catch (error) {
      setErrors(error.response.data);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await logoutRequest();
    setUser(null);
    setIsAuthenticated(false);
    Cookies.remove('access_token');
  };

  useEffect(() => {
  const checkLogin = async () => {
    setLoading(true);
    try {
      const authenticated = await checkAuthRequest();
      if (authenticated) {
        setIsAuthenticated(true);
        setUser({});
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };
  checkLogin();
}, []);


  return (
    <AuthContext.Provider value={{ user, isAuthenticated, loading, errors, signup, signin, logout }}>
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
