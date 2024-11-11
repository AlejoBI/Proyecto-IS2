import { useAuth } from "../context/AuthContext";
import { useNavigate } from 'react-router-dom';
import QuestionForm from "../components/QuestionForm";
import { Container, Button } from "react-bootstrap";
import "../assests/css/HomePage.css"; // Asegúrate de que la ruta sea correcta

const HomePage = () => {
    const { isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
    };

    return (
        <Container className="mt-5 mb-5 p-5 border rounded shadow-lg" style={{ backgroundColor: "white" }}>            <header className="text-center">
                <h1>RAG System</h1>
                <p>Upload a document and ask questions based on its content.</p>
                {!isAuthenticated ? (
                    <Button variant="primary" onClick={() => navigate('/login')}>
                        Go to Login
                    </Button>
                ) : (
                    <Button variant="danger" onClick={handleLogout}>
                        Logout
                    </Button>
                )}
            </header>

            <section>
                <QuestionForm />
            </section>
        </Container>
    );
};

export default HomePage;
