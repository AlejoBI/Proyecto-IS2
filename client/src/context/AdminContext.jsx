import { createContext, useContext, useEffect, useState } from "react";
import {
  createUserRequest,
  updateUserRequest,
  deleteUserRequest,
  getUsersRequest,
  getDocumentsRequest,
  deleteDocumentRequest,
  disableUserRequest,
} from "../api/admin";
import { useAuth } from "./AuthContext";

export const AdminContext = createContext();

export const AdminProvider = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
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

  const editUser = async (userId, updatedData) => {
    setLoading(true);
    try {
      const res = await updateUserRequest(userId, updatedData);
      setUsers((prev) => prev.map((user) => (user.id === userId ? res : user)));
    } catch (error) {
      setErrors(error.response ? error.response.data : error.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (userId) => {
    setLoading(true);
    try {
      await deleteUserRequest(userId);
      setUsers((prev) => prev.filter((user) => user.id !== userId));
    } catch (error) {
      setErrors(error.response ? error.response.data : error.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleUserState = async (userId) => {
    setLoading(true);
    try {
      const user = users.find((user) => user.id === userId);
      const disable = user.state ? true : false;

      const res = await disableUserRequest(user.email, disable);

      setUsers((prev) =>
        prev.map((user) =>
          user.id === userId ? { ...user, state: res.state } : user
        )
      );
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

  useEffect(() => {
    if (isAuthenticated && user.role === "admin") {
      fetchUsers();
    }
  }, [isAuthenticated]);

  return (
    <AdminContext.Provider
      value={{
        users,
        documents,
        loading,
        errors,
        fetchUsers,
        createUser,
        editUser,
        deleteUser,
        toggleUserState,
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
