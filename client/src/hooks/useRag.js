import { useEffect, useState } from "react";
import {
  generateAnswerRequest,
  getSessionDocumentsRequest,
  deleteSessionDocumentRequest,
  indexSessionDocumentRequest,
  getMyHistoryRequest,
  uploadDocumentRequest,
} from "../api/auth";
import { useAuth } from "../context/AuthContext";

export const useRag = () => {
  const [responses, setResponses] = useState([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [documents, setDocuments] = useState([]);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    Promise.all([
      getSessionDocumentsRequest(),
      isAuthenticated ? getMyHistoryRequest() : Promise.resolve([]),
    ])
      .then(([sessionDocuments, history]) => {
        setDocuments(sessionDocuments);
        setResponses(
          [...history].reverse().map(({ question, answer, sources, provider }) => ({
            question,
            answer,
            sources: sources || [],
            provider: provider || "openai",
          })),
        );
      })
      .catch(() => setError("Could not load your saved documents and history."));
  }, [isAuthenticated]);

  const uploadDocument = async (file, apiKey, provider) => {
    if (!file || !apiKey.trim())
      throw new Error("Enter your OpenAI API key and choose a document.");
    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    setError(null);
    setStatus("");
    try {
      const response = await uploadDocumentRequest(formData, apiKey.trim(), provider);
      setStatus(response.status);
      setDocuments(await getSessionDocumentsRequest());
      return response;
    } catch (requestError) {
      const message = requestError.response?.data?.detail || "Error uploading document.";
      setError(message);
      throw requestError;
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (documentId) => {
    setError(null);
    try {
      await deleteSessionDocumentRequest(documentId);
      setDocuments((previous) => previous.filter((document) => document.id !== documentId));
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Error deleting document.");
      throw requestError;
    }
  };

  const indexDocument = async (documentId, apiKey, provider) => {
    if (!apiKey.trim()) {
      const message = "Enter your provider API key first.";
      setError(message);
      throw new Error(message);
    }
    setLoading(true);
    setError(null);
    try {
      await indexSessionDocumentRequest(documentId, apiKey.trim(), provider);
      setDocuments(await getSessionDocumentsRequest());
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Error indexing document.");
      throw requestError;
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async (question, apiKey, provider) => {
    if (!question.trim() || !apiKey.trim()) throw new Error("Enter your API key and a question.");
    setLoading(true);
    setError(null);
    try {
      const result = await generateAnswerRequest(question, apiKey.trim(), provider);
      setResponses((previous) => [
        ...previous,
        {
          question,
          answer: result.answer,
          sources: result.sources || [],
          provider: result.provider || provider,
        },
      ]);
      return result;
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Error generating response.");
      throw requestError;
    } finally {
      setLoading(false);
    }
  };

  return {
    responses,
    documents,
    status,
    loading,
    error,
    uploadDocument,
    askQuestion,
    deleteDocument,
    indexDocument,
  };
};
