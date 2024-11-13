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
export const updateUserRequest = async (updated_data) => {
    const res = await axios.put(`/admin/update-user`, updated_data);
    return res.data;
};

// Eliminar usuario
export const deleteUserRequest = async (email) => {
    const res = await axios.delete(`/admin/delete-user`, {
        params: { email }
    });
    return res.data;
};

// Obtener documentos
export const getDocumentsRequest = async () => {
    const res = await axios.get(`/admin/get-documents`);
    return res.data;
};

// Eliminar documento
export const deleteDocumentRequest = async (document_id) => {
    const res = await axios.delete(`/admin/delete-document`, {
        params: { document_id }
    });
    return res.data;
};
