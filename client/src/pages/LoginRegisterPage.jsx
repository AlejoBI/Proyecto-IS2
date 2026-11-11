import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import FormLogin from "../components/FormLogin";
import FormRegister from "../components/FormRegister";
import Logo from "../assests/images/Logo.jpg";
import { useAuth } from "../context/AuthContext";

const LoginRegisterPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const { errors, setErrors, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) navigate("/");
  }, [isAuthenticated, navigate]);
  useEffect(() => {
    setErrors(null);
  }, [isLogin, setErrors]);

  return (
    <main className="from-brand-700 flex min-h-[calc(100vh-73px)] items-center justify-center bg-gradient-to-br via-slate-950 to-slate-950 px-4 py-12">
      <section className="w-full max-w-md rounded-3xl border border-slate-700 bg-slate-900/95 p-6 shadow-2xl sm:p-9">
        <div className="mb-8 text-center">
          <Link to="/">
            <img
              src={Logo}
              alt="Proyecto IS2"
              className="mx-auto h-16 w-16 rounded-2xl object-cover"
            />
          </Link>
          <h1 className="mt-5 text-3xl font-black text-white">
            {isLogin ? "Welcome back" : "Create your account"}
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            {isLogin
              ? "Sign in to manage your profile."
              : "Registration creates a standard user account."}
          </p>
        </div>
        {errors && (
          <div
            role="alert"
            className="mb-5 rounded-xl border border-red-500/30 bg-red-950/40 px-4 py-3 text-sm text-red-300"
          >
            {errors.detail || errors}
          </div>
        )}
        {isLogin ? <FormLogin /> : <FormRegister />}
        <p className="mt-7 text-center text-sm text-slate-400">
          {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
          <button
            className="text-brand-100 font-semibold hover:text-white"
            onClick={() => setIsLogin((value) => !value)}
          >
            {isLogin ? "Sign up" : "Log in"}
          </button>
        </p>
      </section>
    </main>
  );
};

export default LoginRegisterPage;
