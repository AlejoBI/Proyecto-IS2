import QuestionForm from "../components/QuestionForm";
import {Container} from "react-bootstrap";
import "../assests/css/HomePage.css";

const HomePage = () => {
    return (
        <Container className="mt-5 mb-5 p-5 border rounded bg-light shadow-lg">
            <header className="text-center ">
                <h1>RAG System</h1>
                <p>Upload a document and ask questions based on its content.</p>
            </header>

            <section>
                <QuestionForm/>
            </section>
        </Container>
    );
};

export default HomePage;
