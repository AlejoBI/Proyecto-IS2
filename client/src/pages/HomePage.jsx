import QuestionForm from "../components/QuestionForm";
import { useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import DemoNotice from "../components/DemoNotice";

const HomePage = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      if (user.role !== "user") {
        navigate("/admin/dashboard");
      }
    }
  }, [isAuthenticated, user, navigate]);
  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:py-16">
      <header className="border-brand-500/20 from-brand-700 shadow-brand-950/40 mb-8 rounded-3xl border bg-gradient-to-br to-slate-900 p-8 shadow-2xl sm:p-12">
        <p className="text-brand-100 mb-3 text-sm font-semibold tracking-[0.25em] uppercase">
          Private-by-design RAG
        </p>
        <h1 className="text-4xl font-black tracking-tight text-white sm:text-6xl">
          Ask your documents.
        </h1>
        <p className="text-brand-100 mt-4 max-w-2xl text-lg">
          Upload a document and ask questions using your own OpenAI or Gemini key. Your key is never
          stored by this application.
        </p>
      </header>
      <DemoNotice />
      <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl sm:p-8">
        <QuestionForm />
      </section>

      <section className="mt-10 grid gap-5 lg:grid-cols-3">
        <article className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <div className="bg-brand-500/15 text-brand-100 flex h-11 w-11 items-center justify-center rounded-2xl text-xl">
            1
          </div>
          <h2 className="mt-5 text-xl font-bold text-white">Upload your documents</h2>
          <p className="mt-3 leading-7 text-slate-400">
            Choose a PDF, DOCX or TXT file and provide your own OpenAI or Gemini API key. The
            document is processed into searchable text and vectors.
          </p>
        </article>
        <article className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <div className="bg-brand-500/15 text-brand-100 flex h-11 w-11 items-center justify-center rounded-2xl text-xl">
            2
          </div>
          <h2 className="mt-5 text-xl font-bold text-white">Ask questions</h2>
          <p className="mt-3 leading-7 text-slate-400">
            The RAG engine retrieves the most relevant document fragments and sends only that
            context to the language model to generate an answer with sources.
          </p>
        </article>
        <article className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <div className="bg-brand-500/15 text-brand-100 flex h-11 w-11 items-center justify-center rounded-2xl text-xl">
            3
          </div>
          <h2 className="mt-5 text-xl font-bold text-white">Keep control</h2>
          <p className="mt-3 leading-7 text-slate-400">
            Your API key is used only for requests. Anonymous sessions expire automatically, while
            registered users can recover their own documents and question history.
          </p>
        </article>
      </section>

      <section className="border-brand-500/20 bg-brand-500/5 mt-10 grid gap-5 rounded-3xl border p-6 sm:p-8 lg:grid-cols-2">
        <div>
          <p className="text-brand-100 text-sm font-bold tracking-[0.25em] uppercase">
            Why create an account?
          </p>
          <h2 className="mt-3 text-3xl font-black text-white">
            A personal workspace for your RAG sessions.
          </h2>
          <p className="mt-4 leading-7 text-slate-300">
            You can try the demo without registering. When you create an account and sign in, your
            documents are associated with your email and your answers are saved to your private
            history so you can return to them later.
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          {[
            "Private document library",
            "Saved questions and sources",
            "User-level data isolation",
            "Profile and account controls",
          ].map((benefit) => (
            <div
              key={benefit}
              className="rounded-2xl border border-slate-800 bg-slate-950/50 p-4 text-sm font-semibold text-slate-200"
            >
              <span className="mr-2 text-emerald-400">✓</span>
              {benefit}
            </div>
          ))}
        </div>
      </section>

      <section className="mt-10 rounded-3xl border border-slate-800 bg-slate-950/60 p-6 sm:p-8">
        <p className="text-brand-100 text-sm font-bold tracking-[0.25em] uppercase">
          What happens behind the scenes?
        </p>
        <div className="mt-6 grid gap-6 md:grid-cols-4">
          {[
            ["FastAPI", "Receives requests, validates files and protects user routes."],
            ["MongoDB", "Stores accounts, document metadata and registered-user history."],
            ["ChromaDB", "Indexes document fragments for semantic retrieval."],
            ["OpenAI / Gemini", "Create embeddings and answers using the retrieved context."],
          ].map(([name, description]) => (
            <div key={name}>
              <h3 className="font-bold text-white">{name}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
};

export default HomePage;
