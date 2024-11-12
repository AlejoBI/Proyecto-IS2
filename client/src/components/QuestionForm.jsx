import { useEffect, useState } from "react";
import { uploadDocumentRequest, generateAnswerRequest } from "../api/auth";
import { Form, Button } from "react-bootstrap";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from 'react-router-dom';

const QuestionForm = () => {
    const [file, setFile] = useState(null);
    const [question, setQuestion] = useState("");
    const [status, setStatus] = useState("");
    const [responses, setResponses] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const { isAuthenticated } = useAuth(); 

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleFileUpload = async () => {
        if (!file) return;
        if (!isAuthenticated) {
            setError("You must be logged in to upload documents.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        setLoading(true);
        setStatus("");
        setError(null);

        try {
            const response = await uploadDocumentRequest(formData);
            setStatus(response.status);
        } catch (error) {
            setStatus("Error uploading document");
        } finally {
            setLoading(false);
        }
    };

    const handleAskQuestion = async () => {
        if (question.trim() === "") return;
        if (!isAuthenticated) {
            setError("You must be logged in to ask questions.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const res = await generateAnswerRequest(question);
            setResponses([...responses, { question, answer: res }]);
            setQuestion("");
        } catch (err) {
            setError("Error generating response. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    // Funciones para manejar el clic cuando no está autenticado
    const handleUploadClick = () => {
        if (!isAuthenticated) {
            setError("You must be logged in to upload documents.");
        } else {
            handleFileUpload();
        }
    };

    const handleAskClick = () => {
        if (!isAuthenticated) {
            setError("You must be logged in to ask questions.");
        } else {
            handleAskQuestion();
        }
    };

    useEffect(() => {
        if (!isAuthenticated) {
            setResponses([]);
            setQuestion("");
            setError(null);
        }
    }, [isAuthenticated]);

    return (
        <div>
            <div className="input-group mb-3">
                <Form.Control type="file" onChange={handleFileChange} />
                <Button
                    variant="primary"
                    onClick={handleUploadClick}
                    disabled={loading || !file}
                >
                    {loading ? "Uploading..." : "Upload Document"}
                </Button>
            </div>
            {status && <p>{status}</p>}

            <div className="mt-3 p-3 border rounded bg-light" style={{ height: '400px', overflowY: 'auto' }}>
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
                    disabled={loading}
                />
                <div className="input-group-append">
                    <Button
                        variant="primary"
                        onClick={handleAskClick}
                        disabled={loading || question.trim() === ""}
                    >
                        {loading ? "Processing..." : "Ask"}
                    </Button>
                </div>
            </div>

            {error && <p className="text-danger">{error}</p>}
        </div>
    );
};

export default QuestionForm;
