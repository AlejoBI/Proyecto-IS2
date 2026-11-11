import { useEffect, useState } from "react";
import {
  generateAnswerRequest,
  getMyDocumentsRequest,
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
    if (!isAuthenticated) return;
    Promise.all([getMyDocumentsRequest(), getMyHistoryRequest()])
      .then(([savedDocuments, history]) => {
        setDocuments(savedDocuments);
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
      if (isAuthenticated) setDocuments(await getMyDocumentsRequest());
      return response;
    } catch (requestError) {
      const message = requestError.response?.data?.detail || "Error uploading document.";
      setError(message);
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

  return { responses, documents, status, loading, error, uploadDocument, askQuestion };
};
