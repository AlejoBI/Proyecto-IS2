import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const FormLogin = () => {
  const { signin, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    const success = await signin({
      email: event.target.email.value,
      password: event.target.password.value,
    });
    if (success) navigate("/");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <label className="block text-sm font-semibold text-slate-200">
        Email
        <input
          name="email"
          type="email"
          required
          className="focus:border-brand-500 mt-2 block w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none"
        />
      </label>
      <label className="block text-sm font-semibold text-slate-200">
        Password
        <input
          name="password"
          type="password"
          required
          className="focus:border-brand-500 mt-2 block w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none"
        />
      </label>
      <button
        disabled={loading}
        className="bg-brand-500 hover:bg-brand-600 w-full rounded-xl px-4 py-3 font-bold text-white transition disabled:opacity-50"
      >
        {loading ? "Signing in..." : "Sign in"}
      </button>
    </form>
  );
};

export default FormLogin;
