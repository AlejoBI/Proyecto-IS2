import {useState} from "react";
import {uploadDocumentRequest} from "../api/auth";  // Correcto
import {Form, Button} from "react-bootstrap";

const DocumentUpload = () => {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState("");

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await uploadDocumentRequest(formData);  // Correcto
            setStatus(response.status);
        } catch (error) {
            setStatus("Error uploading document");
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit} className="input-group mb-3">
                <Form.Control type="file" onChange={handleFileChange}/>
                <Button variant="primary" type="submit">
                    Submit
                </Button>
            </form>
            {status && <p>{status}</p>}
        </div>
    );
};

export default DocumentUpload;
