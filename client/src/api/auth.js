import axios from './axios';

export const registerRequest = async (user) => {
    const res = await axios.post(`/register`, user);
    return res.data;
}

export const loginRequest = async (user) => {
    const res = await axios.post(`/login`, user);
    return res.data;
}

export const logoutRequest = () => axios.post(`/logout`);

export const checkAuthRequest = async () => {
    try {
        const res = await axios.get(`/checkauth`);
        return res.data.status === "Authenticated"; // Devuelve true si está autenticado
    } catch (error) {
        return false; // Devuelve false si no está autenticado o si hay un error
    }
};

// Subida de documentos
export const uploadDocumentRequest = async (formData) => {
    const res = await axios.post(`/save-document`, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });
    return res.data;
};

// Generación de respuesta
export const generateAnswerRequest = async (question) => {
    const res = await axios.get(`/generate-answer`, {
        params: {
            query: question,
        }
    });
    return res.data;
};
