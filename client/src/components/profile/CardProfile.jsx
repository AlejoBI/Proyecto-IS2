import { useState } from "react";
import ModalUpdateProfile from "./ModalUpdateProfile";
import ConfirmModal from "../ConfirmModal";
import { useAuth } from "../../context/AuthContext";
import { useAdmin } from "../../context/AdminContext";

const CardProfile = () => {
  const { user } = useAuth();
  const { deleteUser } = useAdmin();
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  return (
    <main className="mx-auto flex min-h-[calc(100vh-73px)] max-w-4xl items-center px-4 py-12">
      <section className="w-full rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-2xl sm:p-12">
        <p className="text-brand-100 text-sm font-bold tracking-[0.25em] uppercase">Account</p>
        <h1 className="mt-3 text-3xl font-black text-white">Your profile</h1>
        <dl className="mt-8 divide-y divide-slate-800">
          <div className="flex justify-between gap-4 py-4">
            <dt className="text-slate-400">Username</dt>
            <dd className="font-semibold text-white">{user?.username}</dd>
          </div>
          <div className="flex justify-between gap-4 py-4">
            <dt className="text-slate-400">Email</dt>
            <dd className="font-semibold text-white">{user?.email}</dd>
          </div>
          <div className="flex justify-between gap-4 py-4">
            <dt className="text-slate-400">Role</dt>
            <dd className="text-brand-100 font-semibold capitalize">{user?.role}</dd>
          </div>
        </dl>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <button
            onClick={() => setShowEditModal(true)}
            className="bg-brand-500 hover:bg-brand-600 flex-1 rounded-xl px-4 py-3 font-bold text-white"
          >
            Edit profile
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="flex-1 rounded-xl border border-red-500/40 px-4 py-3 font-bold text-red-300 hover:bg-red-950/40"
          >
            Delete account
          </button>
        </div>
      </section>
      <ModalUpdateProfile show={showEditModal} onHide={() => setShowEditModal(false)} />
      <ConfirmModal
        show={showDeleteConfirm}
        onConfirm={() => {
          deleteUser(user.email);
          setShowDeleteConfirm(false);
        }}
        onCancel={() => setShowDeleteConfirm(false)}
        message="Are you sure you want to delete your account?"
      />
    </main>
  );
};

export default CardProfile;
