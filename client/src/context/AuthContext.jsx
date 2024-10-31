import { createContext, useContext, useEffect, useState } from "react";
import {
  registerRequest,
  loginRequest,
  logoutRequest,
  checkAuthRequest
} from "../api/auth";
import Cookies from 'js-cookie'; // Asegúrate de instalar js-cookie

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
      // Guardar el token en cookies
      Cookies.set('access_token', res.token, { expires: 1 }); // Ajusta la expiración según sea necesario
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
    Cookies.remove('access_token'); // Eliminar el token de las cookies
  };

  useEffect(() => {
    const checkLogin = async () => {
      setLoading(true);
      try {
        // Verificar si el token está en las cookies
        const token = Cookies.get('access_token');
        if (token) {
          const res = await checkAuthRequest();
          if (res.status === "Authenticated") {
            setUser(res);
            setIsAuthenticated(true);
          } else {
            setIsAuthenticated(false);
          }
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
