import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const FormRegister = () => {
  const { signup, loading } = useAuth();
  const navigate = useNavigate();
  const handleSubmit = async (event) => {
    event.preventDefault();
    const form = event.target;
    await signup({
      username: form.username.value,
      email: form.email.value,
      password: form.password.value,
      confirmPassword: form.confirmPassword.value,
      role: "user",
    });
    navigate("/");
  };
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <label className="block text-sm font-semibold text-slate-200">
        Username
        <input
          name="username"
          minLength="3"
          required
          className="focus:border-brand-500 mt-2 block w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none"
        />
      </label>
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
          minLength="8"
          required
          className="focus:border-brand-500 mt-2 block w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none"
        />
      </label>
      <label className="block text-sm font-semibold text-slate-200">
        Confirm password
        <input
          name="confirmPassword"
          type="password"
          minLength="8"
          required
          className="focus:border-brand-500 mt-2 block w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none"
        />
      </label>
      <button
        disabled={loading}
        className="bg-brand-500 hover:bg-brand-600 w-full rounded-xl px-4 py-3 font-bold text-white transition disabled:opacity-50"
      >
        {loading ? "Creating..." : "Create account"}
      </button>
    </form>
  );
};

export default FormRegister;
