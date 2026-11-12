import { useState } from "react";
import { useRag } from "../hooks/useRag";
import { useRagSession } from "../hooks/useRagSession";
import DemoNotice from "./DemoNotice";

const inputClass =
  "mt-2 block w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20";
const primaryButton =
  "rounded-xl bg-brand-500 px-5 py-3 font-bold text-white transition hover:bg-brand-600 disabled:cursor-not-allowed disabled:opacity-50";

const formatBytes = (bytes) => {
  if (!bytes) return "Size unavailable";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const statusStyles = {
  completed: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  processing: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  pending: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  failed: "border-red-500/30 bg-red-500/10 text-red-300",
};

const QuestionForm = () => {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [provider, setProvider] = useState("openai");
  const [showApiKey, setShowApiKey] = useState(false);
  const { sessionInfo, sessionError } = useRagSession();
  const {
    responses,
    documents,
    status,
    loading,
    error,
    uploadDocument,
    askQuestion,
    deleteDocument,
    indexDocument,
  } = useRag();
  const visibleError = sessionError || error;

  const handleUpload = async () => {
    try {
      await uploadDocument(file, apiKey, provider);
    } catch {
      /* hook exposes the user-facing error */
    }
  };
  const handleAsk = async () => {
    try {
      await askQuestion(question, apiKey, provider);
      setQuestion("");
    } catch {
      /* hook exposes the user-facing error */
    }
  };
  const handleIndex = async (documentId) => {
    try {
      await indexDocument(documentId, apiKey, provider);
    } catch {
      /* hook exposes the user-facing error */
    }
  };

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(280px,0.8fr)_minmax(0,1.4fr)]">
      <aside className="space-y-6 lg:min-w-0">
        <DemoNotice compact />
        <div>
          <label htmlFor="llm-provider" className="text-sm font-semibold text-slate-200">
            AI provider
          </label>
          <select
            id="llm-provider"
            value={provider}
            onChange={(event) => {
              setProvider(event.target.value);
              setApiKey("");
              setShowApiKey(false);
            }}
            className={inputClass}
          >
            <option value="openai">OpenAI</option>
            <option value="gemini">Google Gemini</option>
          </select>
          <p className="mt-2 text-xs text-slate-500">
            You can switch providers between questions. Each answer keeps its provider in the
            history.
          </p>
        </div>
        <div>
          <label htmlFor="api-key" className="text-sm font-semibold text-slate-200">
            {provider === "gemini" ? "Google Gemini API key" : "OpenAI API key"}
          </label>
          <div className="relative mt-2">
            <input
              id="api-key"
              type={showApiKey ? "text" : "password"}
              placeholder={provider === "gemini" ? "AIza..." : "sk-..."}
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
              autoComplete="off"
              className={`${inputClass} mt-0 pr-14`}
            />
            <button
              type="button"
              onClick={() => setShowApiKey((visible) => !visible)}
              aria-label={showApiKey ? "Hide API key" : "Show API key"}
              title={showApiKey ? "Hide API key" : "Show API key"}
              className="absolute inset-y-0 right-0 flex items-center px-4 text-slate-400 transition hover:text-white"
            >
              {showApiKey ? (
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                  className="h-5 w-5 fill-none stroke-current stroke-2"
                >
                  <path d="M3 3l18 18M10.6 10.6a2 2 0 102.8 2.8M9.9 4.2A10.7 10.7 0 0112 4c5 0 8.7 4 10 8a11.8 11.8 0 01-3.1 4.9M6.2 6.2A12 12 0 002 12c1.3 4 5 8 10 8a10.7 10.7 0 004.1-.8" />
                </svg>
              ) : (
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                  className="h-5 w-5 fill-none stroke-current stroke-2"
                >
                  <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" />
                  <circle cx="12" cy="12" r="2.5" />
                </svg>
              )}
            </button>
          </div>
          <p className="mt-2 text-xs text-slate-500">
            Used only for this browser session and never stored by this application.
          </p>
        </div>
        {sessionInfo && (
          <div className="border-brand-500/20 bg-brand-500/10 text-brand-100 rounded-2xl border px-4 py-3 text-sm">
            Session expires {new Date(sessionInfo.expires_at).toLocaleString()} ·{" "}
            {sessionInfo.limits.max_documents} documents · {sessionInfo.limits.max_questions}{" "}
            questions
          </div>
        )}
        <div className="rounded-2xl border border-slate-800 bg-slate-950/50 p-5">
          <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
            <div>
              <h2 className="font-bold text-white">Documents in this session</h2>
              <p className="mt-1 text-xs text-slate-500">
                {documents.length} document{documents.length === 1 ? "" : "s"} · Only completed
                documents can answer questions
              </p>
            </div>
            <span className="text-xs text-slate-500">Provider-specific indexes</span>
          </div>
          {documents.length === 0 ? (
            <p className="mt-4 rounded-xl border border-dashed border-slate-800 px-4 py-5 text-sm text-slate-500">
              No documents uploaded yet. Add a PDF, DOCX or TXT file to start.
            </p>
          ) : (
            <ul className="mt-4 space-y-3">
              {documents.map((document) => {
                const statusClass = statusStyles[document.status] || statusStyles.failed;
                return (
                  <li
                    key={document.id}
                    className="rounded-xl border border-slate-800 bg-slate-900/80 p-4"
                  >
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0">
                        <p className="truncate font-semibold text-slate-100" title={document.title}>
                          📄 {document.title || "Untitled document"}
                        </p>
                        <p className="mt-1 text-xs text-slate-500">
                          {formatBytes(document.size_bytes)}
                          {document.created_at &&
                            ` · ${new Date(document.created_at).toLocaleString()}`}
                          {document.checksum && ` · #${document.checksum}`}
                        </p>
                      </div>
                      <span
                        className={`rounded-full border px-2.5 py-1 text-xs font-semibold uppercase ${statusClass}`}
                      >
                        {document.status}
                      </span>
                    </div>
                    <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                      <span className="rounded-full bg-slate-800 px-2.5 py-1">
                        Indexed: {document.indexed_providers?.join(", ") || "Not indexed"}
                      </span>
                      {document.status === "completed" ? (
                        <span className="text-emerald-300">Ready for questions</span>
                      ) : document.status === "failed" ? (
                        <span className="text-red-300">Upload again to retry processing</span>
                      ) : (
                        <span>Processing document…</span>
                      )}
                      {document.status === "completed" &&
                        !document.indexed_providers?.includes(provider) && (
                          <button
                            type="button"
                            onClick={() => handleIndex(document.id)}
                            disabled={loading}
                            className="text-brand-100 underline-offset-2 transition hover:text-white hover:underline disabled:opacity-50"
                          >
                            Index for {provider === "gemini" ? "Gemini" : "OpenAI"}
                          </button>
                        )}
                      <button
                        type="button"
                        onClick={() => {
                          if (window.confirm(`Remove ${document.title || "this document"}?`)) {
                            deleteDocument(document.id);
                          }
                        }}
                        className="ml-auto text-slate-500 underline-offset-2 transition hover:text-red-300 hover:underline"
                      >
                        Remove
                      </button>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
        <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/50 p-5">
          <label htmlFor="document" className="text-sm font-semibold text-slate-200">
            Document (.pdf, .docx or .txt)
          </label>
          <div className="mt-3 space-y-3">
            <input
              id="document"
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(event) => setFile(event.target.files[0])}
              className={`${inputClass} file:bg-brand-500 mt-0 flex-1 file:mr-4 file:rounded-lg file:border-0 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-white`}
            />
            <button
              onClick={handleUpload}
              disabled={loading || !file}
              className={`${primaryButton} w-full`}
            >
              {loading ? "Uploading..." : "Upload document"}
            </button>
          </div>
          {status && <p className="mt-3 text-sm text-emerald-400">{status}</p>}
        </div>
      </aside>
      <section className="flex min-h-0 flex-col gap-4 lg:sticky lg:top-6 lg:h-[calc(100vh-8rem)] lg:max-h-[800px] lg:min-w-0 lg:self-start">
        <div className="min-h-[320px] min-w-0 flex-1 space-y-4 overflow-y-auto rounded-2xl border border-slate-800 bg-slate-950/70 p-5 lg:min-h-0">
          {responses.length === 0 && (
            <p className="text-sm text-slate-500">
              Your answers and document sources will appear here.
            </p>
          )}
          {responses.map((response, index) => (
            <article
              key={`${response.question}-${index}`}
              className="rounded-2xl border border-slate-800 bg-slate-900 p-4"
            >
              <p className="text-brand-100 text-sm font-semibold">You asked</p>
              <p className="mt-1 text-slate-300">{response.question}</p>
              <p className="text-brand-100 mt-4 text-sm font-semibold">
                Answer · {response.provider === "gemini" ? "Google Gemini" : "OpenAI"}
              </p>
              <p className="mt-1 leading-7 whitespace-pre-wrap text-slate-100">{response.answer}</p>
              {response.sources?.length > 0 && (
                <p className="mt-4 text-xs text-slate-500">
                  Sources:{" "}
                  {response.sources
                    .map((source) => source.title)
                    .filter(Boolean)
                    .join(", ")}
                </p>
              )}
            </article>
          ))}
        </div>
        <div className="flex shrink-0 flex-col gap-3 sm:flex-row">
          <input
            type="text"
            placeholder="Ask a question about your documents..."
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => event.key === "Enter" && handleAsk()}
            disabled={loading}
            className={`${inputClass} !mt-0 h-12 min-w-0 flex-1`}
          />
          <button
            onClick={handleAsk}
            disabled={loading || !question.trim()}
            className={`${primaryButton} h-12 shrink-0 py-0`}
          >
            {loading ? "Processing..." : "Ask question"}
          </button>
        </div>
        {visibleError && (
          <p
            role="alert"
            className="max-h-24 shrink-0 overflow-y-auto rounded-xl border border-red-500/30 bg-red-950/40 px-4 py-3 text-sm text-red-300"
          >
            {visibleError}
          </p>
        )}
      </section>
    </div>
  );
};

export default QuestionForm;
