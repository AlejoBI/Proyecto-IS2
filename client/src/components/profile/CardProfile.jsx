// CardProfile.js
import React, { useState } from "react";
import { Container, Card, Button } from "react-bootstrap";
import ModalUpdateProfile from "./ModalUpdateProfile";
import ConfirmModal from "../ConfirmModal";
import { useAuth } from "../../context/AuthContext";
import { useAdmin } from "../../context/AdminContext";

const CardProfile = () => {
  const { user } = useAuth();
  const { deleteUser } = useAdmin();
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleEditClick = () => {
    setShowEditModal(true);
  };

  const handleDeleteClick = () => {
    setShowDeleteConfirm(true);
  };

  const handleConfirmDelete = () => {
    deleteUser(user.email); 
    setShowDeleteConfirm(false);
  };

  const handleCancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  return (
    <>
      <Container
        style={{
          height: "75vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          background: "#187A6B",
        }}
      >
        <Card className="shadow-lg rounded-5 w-50 d-flex justify-content-center align-items-center p-5">
          <Card.Body className="w-75">
            <div className="text-center mb-4">
              <h2 className="card-title">USER PROFILE</h2>
            </div>
            <p>
              <strong>Nombre de usuario:</strong> {user.username}
            </p>
            <p>
              <strong>Email:</strong> {user.email}
            </p>
            <p>
              <strong>Rol:</strong> {user.role}
            </p>
            <Button
              variant="primary"
              className="w-100 mt-4"
              onClick={handleEditClick}
            >
              EDITAR INFORMACIÓN
            </Button>
            <Button
              variant="secondary"
              className="w-100 mt-2"
              onClick={handleDeleteClick}
            >
              ELIMINAR CUENTA
            </Button>
          </Card.Body>
        </Card>
      </Container>

      <ModalUpdateProfile
        show={showEditModal}
        onHide={() => setShowEditModal(false)}
      />

      <ConfirmModal
        show={showDeleteConfirm}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        message="¿Estás seguro de que quieres eliminar tu cuenta?"
      />
    </>
  );
};

export default CardProfile;
