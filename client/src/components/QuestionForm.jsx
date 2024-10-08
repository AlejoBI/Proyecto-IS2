import {useState} from "react";
import {generateAnswerRequest} from "../api/auth"; // Usar la función que hace la petición de respuesta
import {Button} from "react-bootstrap";

const QuestionForm = () => {
    const [question, setQuestion] = useState("");
    const [responses, setResponses] = useState([]); // Cambiar de 'response' a 'responses' para manejar una lista
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleAskQuestion = async () => {
        if (question.trim() === "") return;

        setLoading(true);
        setError(null);

        try {
            const res = await generateAnswerRequest(question);
            setResponses([...responses, {question, answer: res}]); // Guardar pregunta y respuesta en el estado
            setQuestion(""); // Limpiar el campo de pregunta
        } catch (err) {
            setError("Error generating response. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            {/* Mostrar las preguntas y respuestas como si fuera un chat */}
            <div className="mt-3 p-3 border rounded bg-light" style={{height: '400px', overflowY: 'auto'}}>
                {responses.map((response, index) => (
                    <div key={index} className="mb-3">
                        <div><strong>You:</strong> {response.question}</div>
                        <div><strong>ChatBot:</strong> {response.answer}</div>
                    </div>
                ))}
            </div>
            <br/>
            <div className="input-group mb-3">
                <input
                    type="text"
                    className="form-control"
                    placeholder="Type your question..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                />
                <div className="input-group-append">
                    <Button variant="primary" onClick={handleAskQuestion} disabled={loading}>
                        {loading ? "Asking..." : "Ask"}
                    </Button>
                </div>
            </div>
            {error && <p className="text-danger">{error}</p>}
        </div>
    );
};

export default QuestionForm;
