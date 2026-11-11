import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { useAdmin } from "../../context/AdminContext";
import ConfirmModal from "../ConfirmModal";

const ModalUpdateProfile = ({ show, onHide }) => {
  const { user } = useAuth();
  const { editUser } = useAdmin();
  const [editingUser, setEditingUser] = useState(null);
  const [confirm, setConfirm] = useState(false);
  useEffect(() => {
    if (show)
      setEditingUser({
        username: user.username,
        email: user.email,
        role: user.role,
        isActive: user.isActive,
      });
  }, [show, user]);
  if (!show) return null;
  return (
    <>
      <div
        className="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
      >
        <div className="w-full max-w-lg rounded-3xl border border-slate-700 bg-slate-900 p-6 shadow-2xl">
          <h2 className="text-xl font-bold text-white">Edit profile</h2>
          <label className="mt-6 block text-sm font-semibold text-slate-200">
            Username
            <input
              value={editingUser?.username || ""}
              onChange={(event) => setEditingUser({ ...editingUser, username: event.target.value })}
              className="focus:border-brand-500 mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none"
            />
          </label>
          <div className="mt-6 flex justify-end gap-3">
            <button
              onClick={onHide}
              className="rounded-xl border border-slate-700 px-4 py-2 text-slate-300 hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              onClick={() => setConfirm(true)}
              className="bg-brand-500 hover:bg-brand-600 rounded-xl px-4 py-2 font-bold text-white"
            >
              Save
            </button>
          </div>
        </div>
      </div>
      <ConfirmModal
        show={confirm}
        onConfirm={() => {
          editUser(editingUser);
          setConfirm(false);
          onHide();
        }}
        onCancel={() => setConfirm(false)}
        message="Save these profile changes?"
      />
    </>
  );
};

export default ModalUpdateProfile;
