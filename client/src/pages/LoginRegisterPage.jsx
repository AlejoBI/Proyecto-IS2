import { useAuth } from "../context/AuthContext";
import FormLogin from "../components/FormLogin";
import FormRegister from "../components/FormRegister";
import { Card, Container, Button, Image, Alert } from 'react-bootstrap';
import { useState } from "react";

const LoginRegisterPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const { errors } = useAuth();  // Captura los errores de autenticación

  const handleToggle = () => {
    setIsLogin((prevState) => !prevState);
  };

  return (
    <Container className="d-flex align-items-center justify-content-center min-vh-100 min-vw-100" style={{ background: "linear-gradient(135deg, #1e3c72, #2a5298)" }}>
      <Card className="shadow-lg rounded-5 w-50 h-50 d-flex justify-content-center align-items-center">
        <Card.Body className="w-50 h-50">
          <div className="text-center mb-4">
            <Image src="path-to-logo" alt="Logo" className="img-fluid" style={{ width: "80px", height: "80px" }} />
            <h2 className="card-title">{isLogin ? "Login" : "Register"}</h2>
            {errors && <Alert variant="danger">{errors.detail}</Alert>} {/* Muestra errores */}
          </div>
          {isLogin ? <FormLogin /> : <FormRegister />}
          <p className="text-muted">
            {isLogin ? "Don't you have an account?" : "Already have an account?"}
            <button className="btn-link text-primary" onClick={handleToggle} style={{ border: "none", background: "none", cursor: "pointer" }}>
              {isLogin ? "Sign up" : "Log in"}
            </button>
          </p>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default LoginRegisterPage;
