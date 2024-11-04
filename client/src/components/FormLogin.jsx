import { useAuth } from "../context/AuthContext"; // Importa tu contexto de autenticación
import { Form, Button, Container } from "react-bootstrap"; // Importa componentes de react-bootstrap
import { useNavigate } from 'react-router-dom'; // Importa useNavigate

const FormLogin = () => {
    const { signin, errors } = useAuth(); // Desestructura la función signin y los errores del contexto
    const navigate = useNavigate(); // Inicializa useNavigate

    const handleSubmit = async (e) => {
        e.preventDefault(); // Previene el comportamiento por defecto del formulario
        const email = e.target.email.value; // Obtiene el email
        const password = e.target.password.value; // Obtiene la contraseña

        const data = { email, password }; // Crea un objeto con los datos del formulario
        const success = await signin(data); // Espera el resultado del signin

        if (success) {
            navigate('/'); // Redirige a la HomePage en caso de éxito
        } else {
            console.error("Error en la autenticación"); // Maneja el error (puedes mostrar un mensaje al usuario)
        }
    };

    return (
        <Container className="p-4">
            <Form onSubmit={handleSubmit}>
                <Form.Group controlId="email" className="mb-3">
                    <Form.Label>Email address</Form.Label>
                    <Form.Control
                        type="email"
                        placeholder="Enter email"
                        name="email"
                        required
                    />
                </Form.Group>

                <Form.Group controlId="password" className="mb-3">
                    <Form.Label>Password</Form.Label>
                    <Form.Control
                        type="password"
                        placeholder="Enter password"
                        name="password"
                        required
                    />
                </Form.Group>

                {errors && <div className="alert alert-danger">{errors}</div>} {/* Muestra errores si hay */}

                <Button
                    variant="primary"
                    type="submit"
                    className="w-100"
                    style={{ backgroundColor: "#007bff", borderColor: "#007bff" }}>
                    Login
                </Button>
            </Form>
        </Container>
    );
};

export default FormLogin;
