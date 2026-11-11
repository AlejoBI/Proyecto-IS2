import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import Logo from "../assests/images/Logo.jpg";

const NavbarComponent = () => {
  const { isAuthenticated, logout, user } = useAuth();
  const [open, setOpen] = useState(false);
  const title = user ? `${user.username}` : "Home";

  return (
    <nav className="sticky top-0 z-40 border-b border-slate-800 bg-slate-950/90 px-4 py-3 backdrop-blur sm:px-6">
      <div className="mx-auto flex max-w-6xl items-center justify-between">
        <a href="/" className="flex items-center gap-3">
          <img
            src={Logo}
            alt="Proyecto IS2"
            className="ring-brand-500/40 h-11 w-11 rounded-xl object-cover ring-2"
          />
          <span className="hidden text-sm font-bold tracking-wide text-white sm:block">
            PROYECTO IS2
          </span>
        </a>
        <div className="relative">
          {isAuthenticated ? (
            <>
              <button
                onClick={() => setOpen(!open)}
                className="hover:border-brand-500 rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition"
              >
                {title} <span className="ml-2 text-slate-400">⌄</span>
              </button>
              {open && (
                <div className="absolute right-0 mt-2 w-48 rounded-2xl border border-slate-700 bg-slate-900 p-2 shadow-2xl">
                  {user?.role === "user" && (
                    <a
                      href="/user/profile"
                      className="block rounded-xl px-3 py-2 text-sm text-slate-200 hover:bg-slate-800"
                    >
                      Profile
                    </a>
                  )}
                  <button
                    onClick={logout}
                    className="block w-full rounded-xl px-3 py-2 text-left text-sm text-red-300 hover:bg-red-950/40"
                  >
                    Logout
                  </button>
                </div>
              )}
            </>
          ) : (
            <a
              href="/login"
              className="bg-brand-500 shadow-brand-950/40 hover:bg-brand-600 rounded-xl px-4 py-2 text-sm font-bold text-white shadow-lg transition"
            >
              Login
            </a>
          )}
        </div>
      </div>
    </nav>
  );
};

export default NavbarComponent;
