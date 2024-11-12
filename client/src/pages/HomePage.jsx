import QuestionForm from "../components/QuestionForm";
import { Container } from "react-bootstrap";
import "../assests/css/HomePage.css";
import { useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      if (user.role !== "user") {
        navigate("/admin/dashboard");
      }
    }
  }, [isAuthenticated, user]);
  return (
    <Container
      className="mt-5 mb-5 p-5 border rounded shadow-lg"
      style={{ backgroundColor: "white" }}
    >
      {" "}
      <header className="text-center">
        <h1>RAG System</h1>
        <p>Upload a document and ask questions based on its content.</p>
      </header>
      <section>
        <QuestionForm />
      </section>
    </Container>
  );
};

export default HomePage;
