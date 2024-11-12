import axios from './axios';

// Obtener usuarios
export const getUsersRequest = async () => {
    const res = await axios.get(`/admin/get-users`);
    return res.data;
};

// Crear usuario
export const createUserRequest = async (user) => {
    const res = await axios.post(`/admin/save-user`, user);
    return res.data;
};

// Deshabilitar o habilitar usuario
export const disableUserRequest = async (email, disable = true) => {
    const res = await axios.post(`/admin/disable-user`, { email, disable });
    return res.data;
};

// Editar usuario
export const updateUserRequest = async (email, updatedData) => {
    const res = await axios.put(`/admin/update-user`, { email, updatedData });
    return res.data;
};

// Eliminar usuario
export const deleteUserRequest = async (email) => {
    const res = await axios.delete(`/admin/delete-user`, { data: { email } });
    return res.data;
};

// Obtener documentos
export const getDocumentsRequest = async () => {
    const res = await axios.get(`/admin/get-documents`);
    return res.data;
};

// Eliminar documento
export const deleteDocumentRequest = async (documentId) => {
    const res = await axios.delete(`/admin/delete-document`, { data: { document_id: documentId } });
    return res.data;
};
