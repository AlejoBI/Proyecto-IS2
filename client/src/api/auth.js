import axios from "./axios";

export const registerRequest = async (user) => {
  const res = await axios.post(`/register`, user);
  return res.data;
};

export const loginRequest = async (user) => {
  const res = await axios.post(`/login`, user);
  return res.data;
};

export const logoutRequest = () => axios.post(`/logout`);

export const checkAuthRequest = async () => {
  try {
    const res = await axios.get(`/checkauth`);
    return res.data;
  } catch {
    return null;
  }
};

// Subida de documentos
export const createSessionRequest = async () => {
  const res = await axios.get(`/session`);
  return res.data;
};

export const generateAnswerRequest = async (question, apiKey, provider = "openai") => {
  const res = await axios.get(`/generate-answer`, {
    params: {
      query: question,
    },
    headers: { "X-LLM-API-Key": apiKey, "X-LLM-Provider": provider },
  });
  return res.data;
};

export const uploadDocumentRequest = async (formData, apiKey, provider = "openai") => {
  const res = await axios.post(`/save-document`, formData, {
    headers: { "X-LLM-API-Key": apiKey, "X-LLM-Provider": provider },
  });
  return res.data;
};

export const getMyDocumentsRequest = async () => {
  const res = await axios.get(`/me/documents`);
  return res.data;
};

export const getMyHistoryRequest = async () => {
  const res = await axios.get(`/me/history`);
  return res.data;
};
