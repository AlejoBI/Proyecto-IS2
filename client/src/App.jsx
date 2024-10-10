import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import 'bootstrap/dist/css/bootstrap.min.css';

import PublicRoute from "./utils/PublicRoute";
import ProtectedRoute from "./utils/ProtectedRoute";

import NotFoundPage from "./pages/NotFoundPage";
import AdminDashboard from "./pages/AdminDashboard";
import HomePage from "./pages/HomePage";
import LoginRegisterPage from "./pages/LoginRegisterPage";
import ProfilePage from "./pages/ProfilePage";

import Navbar from "./components/Navbar";

function Layout({ children }) {
  const location = useLocation();

  const showNav = !["/login"].includes(location.pathname);

  return (
    <>
      {showNav && <Navbar />}
      {children}
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
            <Route
              path="/"
              element={
                <Layout>
                  <HomePage />
                </Layout>
              }
            />
            
          <Route element={<PublicRoute />}>
            <Route
              path="/login"
              element={
                <Layout>
                  <LoginRegisterPage />
                </Layout>
              }
            />
          </Route>

          <Route element={<ProtectedRoute />}>
            <Route
              path="/admin/dashboard"
              element={
                <Layout>
                  <AdminDashboard />
                </Layout>
              }
            />
            <Route
              path="/user/profile"
              element={
                <Layout>
                  <ProfilePage />
                </Layout>
              }
            />
          </Route>

          <Route
            path="*"
            element={
              <Layout>
                <NotFoundPage />
              </Layout>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
