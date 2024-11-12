import { createContext, useContext, useEffect, useState } from "react";
import {
  registerRequest,
  loginRequest,
  logoutRequest,
  checkAuthRequest,
} from "../api/auth";
import Cookies from "js-cookie";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState({});
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [errors, setErrors] = useState(null);

  const signup = async (user) => {
    setLoading(true);
    try {
      if (user.username.length < 3) {
        setErrors("Username must be at least 3 characters long");
        return;
      }

      if (user.email.length < 3) {
        setErrors("Email must be at least 3 characters long");
        return;
      }

      if (user.password !== user.confirmPassword) {
        setErrors("Passwords do not match");
        return;
      }

      if (user.password.length < 6) {
        setErrors("Password must be at least 6 characters long");
        return;
      }

      await registerRequest(user);
    } catch (error) {
      setErrors(error.response ? error.response.data : error.message);
    } finally {
      setLoading(false);
    }
  };

  const signin = async (user) => {
    setLoading(true);
    try {
      const res = await loginRequest(user);
      sessionStorage.setItem("user", JSON.stringify(res));
      setUser(res);
      setIsAuthenticated(true);
      Cookies.set("access_token", res.token, { expires: 1 });
      return true;
    } catch (error) {
      setErrors(error.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await logoutRequest();
    setUser(null);
    setIsAuthenticated(false);
    Cookies.remove("access_token");
    sessionStorage.removeItem("user");
  };

  useEffect(() => {
    const checkLogin = async () => {
      setLoading(true);
      try {
        const authenticated = await checkAuthRequest();
        if (authenticated) {
          setIsAuthenticated(true);
          const infoUser = sessionStorage.getItem("user");
          if (infoUser) {
            setUser(JSON.parse(infoUser));
          }
        } else {
          sessionStorage.removeItem("user");
          setIsAuthenticated(false);
        }
      } catch (error) {
        sessionStorage.removeItem("user");
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };
    checkLogin();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        errors,
        setErrors,
        signup,
        signin,
        logout,
      }}
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
