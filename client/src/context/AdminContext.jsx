import { createContext, useContext, useState } from "react";
import {
  createUserRequest,
  updateUserRequest,
  deleteUserRequest,
  getUsersRequest,
  getDocumentsRequest,
  deleteDocumentRequest,
} from "../api/admin";

import { useAuth } from "./AuthContext";

export const AdminContext = createContext();

export const AdminProvider = ({ children }) => {
  const { user, setUser, logout } = useAuth();
  const [users, setUsers] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState(null);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await getUsersRequest();
      setUsers(res);
    } catch (error) {
      setErrors(error.response ? error.response.data : error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const res = await getDocumentsRequest();
      setDocuments(res);
    } catch (error) {
      setErrors(error.response ? error.response.data : error.message);
    } finally {
      setLoading(false);
    }
  };

  const createUser = async (user) => {
    setLoading(true);
    try {
      const res = await createUserRequest(user);
      setUsers((prev) => [...prev, res]);
    } catch (error) {
      setErrors(error.response ? error.response.data : error.message);
    } finally {
      setLoading(false);
    }
  };

  const editUser = async (updatedData) => {
    setLoading(true);
    try {
      await updateUserRequest(updatedData);
      setUsers((prev) =>
        prev.map((user) =>
          user.email === updatedData.email ? updatedData : user
        )
      );
      if (user.email === updatedData.email && user.role !== "admin") {
        setUser(updatedData);
        sessionStorage.setItem("user", JSON.stringify(updatedData));
      }
    } catch (error) {
      setErrors(error.response ? error.response.data : error.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (userEmail) => {
    setLoading(true);
    try {
      await deleteUserRequest(userEmail);
      setUsers((prev) => prev.filter((user) => user.email !== userEmail));
      if (user.role !== "admin") {
        logout();
      }
    } catch (error) {
      setErrors(error.response ? error.response.data : error.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (documentId) => {
    setLoading(true);
    try {
      await deleteDocumentRequest(documentId);
      setDocuments((prev) => prev.filter((doc) => doc.id !== documentId));
    } catch (error) {
      setErrors(error.response ? error.response.data : error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AdminContext.Provider
      value={{
        users,
        documents,
        loading,
        errors,
        setErrors,
        fetchUsers,
        createUser,
        editUser,
        deleteUser,
        fetchDocuments,
        deleteDocument,
      }}
    >
      {children}
    </AdminContext.Provider>
  );
};

export const useAdmin = () => {
  const context = useContext(AdminContext);
  if (!context) {
    throw new Error("useAdmin must be used within an AdminProvider");
  }
  return context;
};
