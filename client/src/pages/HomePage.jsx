import DocumentUpload from "../components/DocumentUpload";
import QuestionForm from "../components/QuestionForm";

const HomePage = () => {
  return (
      <div className="container mt-5 mb-5 p-5 border rounded shadow-sm bg-light">
          <header className="mb-4 text-center">
              <h1>RAG System</h1>
              <p>Upload a document and ask questions based on its content.</p>
          </header>

          <div>
              <QuestionForm/>
          </div>

          <div className="mb-5">
              <DocumentUpload/>
          </div>
      </div>
  );
};

export default HomePage;
