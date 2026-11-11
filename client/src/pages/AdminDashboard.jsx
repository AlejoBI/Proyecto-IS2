import { useEffect, useState } from "react";
import ConfirmModal from "../components/ConfirmModal";
import { useAdmin } from "../context/AdminContext";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const AdminDashboard = () => {
  const {
    users,
    documents,
    loading,
    errors,
    editUser,
    deleteUser,
    deleteDocument,
    fetchUsers,
    fetchDocuments,
    setErrors,
  } = useAdmin();
  const { isAuthenticated, user } = useAuth();
  const [section, setSection] = useState("users");
  const [editingUser, setEditingUser] = useState(null);
  const [confirmUser, setConfirmUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated || user?.role !== "admin") navigate("/");
  }, [isAuthenticated, user, navigate]);
  useEffect(() => {
    section === "users" ? fetchUsers() : fetchDocuments();
  }, [section]);
  useEffect(() => () => setErrors(null), [setErrors]);

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <p className="text-brand-100 text-sm font-bold tracking-[0.25em] uppercase">
            Control center
          </p>
          <h1 className="mt-2 text-4xl font-black text-white">Admin dashboard</h1>
        </div>
        <div className="flex rounded-xl border border-slate-700 bg-slate-900 p-1">
          <button
            onClick={() => setSection("users")}
            className={`rounded-lg px-4 py-2 text-sm font-semibold ${section === "users" ? "bg-brand-500 text-white" : "text-slate-400"}`}
          >
            Users
          </button>
          <button
            onClick={() => setSection("documents")}
            className={`rounded-lg px-4 py-2 text-sm font-semibold ${section === "documents" ? "bg-brand-500 text-white" : "text-slate-400"}`}
          >
            Documents
          </button>
        </div>
      </div>
      {errors && (
        <div className="mt-6 rounded-xl border border-red-500/30 bg-red-950/40 px-4 py-3 text-sm text-red-300">
          {errors.detail || errors}
        </div>
      )}
      {loading ? (
        <div className="mt-10">
          <div className="border-t-brand-500 h-10 w-10 animate-spin rounded-full border-4 border-slate-700" />
        </div>
      ) : (
        <div className="mt-8 overflow-hidden rounded-3xl border border-slate-800 bg-slate-900 shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-800 bg-slate-950/60 text-xs tracking-wider text-slate-500 uppercase">
                <tr>
                  {section === "users" ? (
                    <>
                      <th className="px-5 py-4">Username</th>
                      <th className="px-5 py-4">Email</th>
                      <th className="px-5 py-4">State</th>
                      <th className="px-5 py-4">Role</th>
                      <th className="px-5 py-4">Actions</th>
                    </>
                  ) : (
                    <>
                      <th className="px-5 py-4">Document</th>
                      <th className="px-5 py-4">Path</th>
                      <th className="px-5 py-4">Actions</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {section === "users"
                  ? users
                      .filter((item) => item.email !== user?.email)
                      .map((item) => (
                        <tr key={item._id} className="hover:bg-slate-800/40">
                          <td className="px-5 py-4 font-semibold text-white">{item.username}</td>
                          <td className="px-5 py-4 text-slate-400">{item.email}</td>
                          <td className="px-5 py-4">
                            {item.isActive ? (
                              <span className="text-emerald-400">Active</span>
                            ) : (
                              <span className="text-red-400">Inactive</span>
                            )}
                          </td>
                          <td className="text-brand-100 px-5 py-4 capitalize">{item.role}</td>
                          <td className="px-5 py-4">
                            <button
                              onClick={() => setEditingUser(item)}
                              className="text-brand-100 mr-3 hover:text-white"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => setConfirmUser(item.email)}
                              className="text-red-300 hover:text-red-200"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))
                  : documents.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-800/40">
                        <td className="px-5 py-4 font-semibold text-white">{item.title}</td>
                        <td className="px-5 py-4 text-slate-400">{item.path}</td>
                        <td className="px-5 py-4">
                          <button
                            onClick={() => deleteDocument(item.id)}
                            className="text-red-300 hover:text-red-200"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {editingUser && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-3xl border border-slate-700 bg-slate-900 p-6 shadow-2xl">
            <h2 className="text-xl font-bold text-white">Edit user</h2>
            <input
              value={editingUser.username}
              onChange={(event) => setEditingUser({ ...editingUser, username: event.target.value })}
              className="mt-5 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white"
            />
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setEditingUser(null)}
                className="rounded-xl border border-slate-700 px-4 py-2 text-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  editUser(editingUser);
                  setEditingUser(null);
                }}
                className="bg-brand-500 rounded-xl px-4 py-2 font-bold text-white"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
      <ConfirmModal
        show={Boolean(confirmUser)}
        onConfirm={() => {
          deleteUser(confirmUser);
          setConfirmUser(null);
        }}
        onCancel={() => setConfirmUser(null)}
        message="Delete this user?"
      />
    </main>
  );
};

export default AdminDashboard;
