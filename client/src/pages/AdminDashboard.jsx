import React, { useState, useEffect } from "react";
import { Modal, Button, Dropdown, Alert } from "react-bootstrap";
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
    toggleUserState,
    fetchDocuments,
  } = useAdmin();
  const { isAuthenticated, user } = useAuth();
  const [editingUser, setEditingUser] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);
  const [newState, setNewState] = useState(null);
  const [newRole, setNewRole] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    if (!isAuthenticated || user.role !== "admin") {
      navigate("/");
    }
  }, [isAuthenticated, user]);

  const handleEditUser = (user) => {
    setEditingUser(user);
  };

  const handleDeleteUser = (userId) => {
    setUserToDelete(userId);
    setShowConfirmModal(true);
  };

  const handleStateChange = (userId) => {
    toggleUserState(userId);
  };

  const handleRoleChange = (userId, newRole) => {
    editUser(userId, { role: newRole });
  };

  const handleConfirmDelete = () => {
    deleteUser(userToDelete);
    setShowConfirmModal(false);
  };

  const handleCancelDelete = () => {
    setShowConfirmModal(false);
  };

  const handleSaveEdit = () => {
    if (editingUser) {
      editUser(editingUser.id, {
        username: editingUser.username,
        email: editingUser.email,
        role: newRole || editingUser.role,
        state: newState || editingUser.state,
      });
      setEditingUser(null);
    }
  };

  return (
    <div className="container mt-4">
      <h1>Admin Dashboard</h1>
      {loading && <p>Loading...</p>}
      {errors && (
        <Alert variant="danger">
          {errors && errors.detail ? errors.detail : errors}
        </Alert>
      )}
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
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td>
                <Dropdown
                  onSelect={(selectedState) => setNewState(selectedState)}
                >
                  <Dropdown.Toggle variant="success" id="dropdown-basic">
                    {user.state}
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item eventKey="active">Active</Dropdown.Item>
                    <Dropdown.Item eventKey="inactive">Inactive</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </td>
              <td>
                <Dropdown onSelect={(selectedRole) => setNewRole(selectedRole)}>
                  <Dropdown.Toggle variant="success" id="dropdown-basic">
                    {user.role}
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item eventKey="user">User</Dropdown.Item>
                    <Dropdown.Item eventKey="admin">Admin</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </td>
              <td>
                <button
                  className="btn btn-warning mr-2"
                  onClick={() => handleEditUser(user)}
                >
                  Edit
                </button>
                <button
                  className="btn btn-danger"
                  onClick={() => handleDeleteUser(user.id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

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
                onChange={(e) =>
                  setEditingUser({ ...editingUser, username: e.target.value })
                }
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                className="form-control"
                value={editingUser.email}
                onChange={(e) =>
                  setEditingUser({ ...editingUser, email: e.target.value })
                }
              />
            </div>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setEditingUser(null)}>
              Close
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
    </div>
  );
};

export default AdminDashboard;
