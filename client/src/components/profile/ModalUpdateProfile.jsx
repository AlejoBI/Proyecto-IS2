// ModalUpdateProfile.js
import React, { useState, useEffect } from "react";
import { Modal, Button } from "react-bootstrap";
import { useAuth } from "../../context/AuthContext";
import { useAdmin } from "../../context/AdminContext";
import ConfirmModal from "../ConfirmModal";

const ModalUpdateProfile = ({ show, onHide }) => {
  const { user } = useAuth();
  const { editUser } = useAdmin();
  const [editingUser, setEditingUser] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const inforUser = {
    username: user.username,
    email: user.email,
    password: user.password,
    role: user.role,
    isActive: user.isActive,
  };

  useEffect(() => {
    if (show) setEditingUser(inforUser);
  }, [show, user]);

  const handleSaveEdit = () => {
    setShowConfirmModal(true);
  };

  const handleConfirmSave = () => {
    editUser(editingUser);
    setShowConfirmModal(false);
    onHide();
  };

  const handleCancelSave = () => {
    setShowConfirmModal(false);
  };

  return (
    <>
      <Modal show={show} onHide={onHide}>
        <Modal.Header closeButton>
          <Modal.Title>Editar Usuario</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="form-group">
            <label>Nombre de usuario</label>
            <input
              type="text"
              className="form-control"
              value={editingUser?.username || ""}
              onChange={(e) =>
                setEditingUser({ ...editingUser, username: e.target.value })
              }
            />
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onHide}>
            Cancelar
          </Button>
          <Button variant="primary" onClick={handleSaveEdit}>
            Guardar Cambios
          </Button>
        </Modal.Footer>
      </Modal>

      <ConfirmModal
        show={showConfirmModal}
        onConfirm={handleConfirmSave}
        onCancel={handleCancelSave}
        message="¿Estás seguro de que quieres guardar estos cambios?"
      />
    </>
  );
};

export default ModalUpdateProfile;
