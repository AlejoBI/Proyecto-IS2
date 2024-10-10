import {useState} from "react";
import {uploadDocumentRequest, generateAnswerRequest} from "../api/auth";  // Ambas funciones de API
import {Form, Button} from "react-bootstrap";

const QuestionForm = () => {
    const [file, setFile] = useState(null);
    const [question, setQuestion] = useState("");
    const [status, setStatus] = useState("");
    const [responses, setResponses] = useState([]);
    const [loading, setLoading] = useState(false);  // Controla el estado de carga, usado tanto para la subida como para la pregunta
    const [error, setError] = useState(null);

    // Maneja el cambio del archivo
    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    // Maneja la subida del archivo
    const handleFileUpload = async () => {
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        setLoading(true);  // Inicia la carga
        setStatus("");
        setError(null);

        try {
            const response = await uploadDocumentRequest(formData);
            setStatus(response.status);
        } catch (error) {
            setStatus("Error uploading document");
        } finally {
            setLoading(false);  // Termina la carga, habilita de nuevo la capacidad de hacer preguntas
        }
    };

    // Maneja la generación de respuestas
    const handleAskQuestion = async () => {
        if (question.trim() === "") return;  // No se permite hacer preguntas vacías

        setLoading(true);  // Inicia la carga para la pregunta
        setError(null);

        try {
            const res = await generateAnswerRequest(question);
            setResponses([...responses, { question, answer: res }]);
            setQuestion("");  // Limpia el campo de pregunta
        } catch (err) {
            setError("Error generating response. Please try again.");
        } finally {
            setLoading(false);  // Termina la carga
        }
    };

    return (
        <div>
            {/* Formulario para subir archivo */}
            <div className="input-group mb-3">
                <Form.Control type="file" onChange={handleFileChange} />
                <Button
                    variant="primary"
                    onClick={handleFileUpload}
                    disabled={loading || !file}  // Deshabilita si ya está cargando o no hay archivo seleccionado
                >
                    {loading ? "Uploading..." : "Upload Document"}
                </Button>
            </div>
            {status && <p>{status}</p>}

            {/* Mostrar preguntas y respuestas estilo chat */}
            <div className="mt-3 p-3 border rounded bg-light" style={{ height: '400px', overflowY: 'auto' }}>
                {responses.map((response, index) => (
                    <div key={index} className="mb-3">
                        <div><strong>You:</strong> {response.question}</div>
                        <div><strong>ChatBot:</strong> {response.answer}</div>
                    </div>
                ))}
            </div>

            <br/>

            {/* Campo de entrada para la pregunta */}
            <div className="input-group mb-3">
                <input
                    type="text"
                    className="form-control"
                    placeholder="Type your question..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    disabled={loading}  // Deshabilita mientras se está subiendo un archivo o generando una respuesta
                />
                <div className="input-group-append">
                    <Button
                        variant="primary"
                        onClick={handleAskQuestion}
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
