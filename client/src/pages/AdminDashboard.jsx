import React, { useState, useEffect } from "react";
import { Modal, Button, Dropdown, Alert, Container } from "react-bootstrap";
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
  } = useAdmin();
  const { isAuthenticated, user, setErrors } = useAuth();
  const [editingUser, setEditingUser] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);
  const [newState, setNewState] = useState(null);
  const [newRole, setNewRole] = useState(null);
  const [caseSelected, setCaseSelected] = useState("users");
  const navigate = useNavigate();

  const currentUserEmail = user ? user.email : null;

  useEffect(() => {
    if (!isAuthenticated || user.role !== "admin") {
      navigate("/");
    }
  }, [isAuthenticated, user, navigate]);

  useEffect(() => {
    if (caseSelected === "users") {
      fetchUsers();
    } else if (caseSelected === "documents") {
      fetchDocuments();
    }
  }, [caseSelected]);

  useEffect(() => {
    setErrors(null);
  }, [caseSelected, users, documents, setErrors]);

  const handleEditUser = (user) => {
    setEditingUser(user);
    setNewState(user.isActive ? "active" : "inactive");
    setNewRole(user.role);
  };

  const handleDeleteUser = (userId) => {
    setUserToDelete(userId);
    setShowConfirmModal(true);
  };

  const handleStateChange = (selectedState) => {
    setNewState(selectedState);
  };

  const handleRoleChange = (selectedRole) => {
    setNewRole(selectedRole);
  };

  const handleConfirmDelete = () => {
    deleteUser(userToDelete);
    setShowConfirmModal(false);
  };

  const handleCancelDelete = () => {
    setShowConfirmModal(false);
  };

  const handleDeleteDocument = (documentId) => {
    deleteDocument(documentId);
  };

  const handleSaveEdit = () => {
    if (editingUser) {
      const updatedUser = {
        ...editingUser,
        role: newRole || editingUser.role,
        isActive: newState === "active" ? true : false,
      };

      if (!updatedUser.role || typeof updatedUser.isActive !== "boolean") {
        console.error("Role or state is invalid");
        return;
      }

      try {
        editUser(updatedUser);
        setEditingUser(null);
        setNewState(null);
        setNewRole(null);
      } catch (error) {
        console.error("Error updating user:", error);
      }
    }
  };

  return (
    <Container
      className="mt-5 mb-5 p-5 border rounded shadow-lg"
      style={{ backgroundColor: "white" }}
    >
      <h1>Admin Dashboard</h1>

      <div className="d-flex justify-content-between align-items-center mb-3">
        <Dropdown onSelect={(eventKey) => setCaseSelected(eventKey)}>
          <Dropdown.Toggle variant="secondary" id="dropdown-basic">
            {caseSelected === "users" ? "Manage Users" : "Manage Documents"}
          </Dropdown.Toggle>
          <Dropdown.Menu>
            <Dropdown.Item eventKey="users">Users</Dropdown.Item>
            <Dropdown.Item eventKey="documents">Documents</Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      </div>

      {loading && <p>Loading...</p>}
      {errors && (
        <Alert variant="danger">
          {errors && errors.detail ? errors.detail : errors}
        </Alert>
      )}

      {caseSelected === "users" ? (
        <table className="table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>State</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users && users.length > 0 ? (
              users.map(
                (user) =>
                  user.email !== currentUserEmail && (
                    <tr key={user._id}>
                      <td>{user.username}</td>
                      <td>{user.email}</td>
                      <td>{user.isActive ? "Active" : "Inactive"}</td>
                      <td>{user.role}</td>
                      <td>
                        <button
                          className="btn btn-warning mr-2"
                          onClick={() => handleEditUser(user)}
                        >
                          Edit
                        </button>{" "}
                        <button
                          className="btn btn-danger"
                          onClick={() => handleDeleteUser(user.email)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  )
              )
            ) : (
              <tr>
                <td colSpan="5">No users found</td>
              </tr>
            )}
          </tbody>
        </table>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Document Name</th>
              <th>Path</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents && documents.length > 0 ? (
              documents.map((document) => (
                <tr key={document.id}>
                  <td>{document.title}</td>
                  <td>{document.path}</td>
                  <td>
                    <button
                      className="btn btn-danger"
                      onClick={() => handleDeleteDocument(document.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4">No documents found</td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      {editingUser && (
        <Modal show={!!editingUser} onHide={() => setEditingUser(null)}>
          <Modal.Header closeButton>
            <Modal.Title>Edit User</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                className="form-control"
                value={editingUser.username}
                onChange={(e) => {
                  setEditingUser({ ...editingUser, username: e.target.value });
                }}
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                className="form-control"
                value={editingUser.email}
                onChange={(e) => {
                  setEditingUser({ ...editingUser, email: e.target.value });
                }}
                disabled
              />
            </div>
            <div className="form-group">
              <label>State</label>
              <Dropdown
                onSelect={handleStateChange}
                value={
                  newState || (editingUser.isActive ? "active" : "inactive")
                }
              >
                <Dropdown.Toggle
                  variant={newState === "active" ? "primary" : "danger"}
                >
                  {newState === "active" ? "Active" : "Inactive"}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item eventKey="active">Active</Dropdown.Item>
                  <Dropdown.Item eventKey="inactive">Inactive</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </div>
            <div className="form-group">
              <label>Role</label>
              <Dropdown
                onSelect={handleRoleChange}
                value={newRole || editingUser.role}
              >
                <Dropdown.Toggle variant="success">
                  {newRole || editingUser.role}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item eventKey="user">User</Dropdown.Item>
                  <Dropdown.Item eventKey="admin">Admin</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </div>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setEditingUser(null)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSaveEdit}>
              Save Changes
            </Button>
          </Modal.Footer>
        </Modal>
      )}

      <ConfirmModal
        show={showConfirmModal}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        message="Are you sure you want to delete this user?"
      />
    </Container>
  );
};

export default AdminDashboard;
