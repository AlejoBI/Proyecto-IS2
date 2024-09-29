import { useState } from "react";
import FormLogin from "../components/FormLogin";
import FormRegister from "../components/FormRegister";
import { Card, Container, Button, Image } from 'react-bootstrap';

const LoginRegisterPage = () => {
  const [isLogin, setIsLogin] = useState(true);

  const handleToggle = () => {
    setIsLogin((prevState) => !prevState);
  };

  const title = isLogin ? "Login" : "Register";

  return (
    <Container className="d-flex align-items-center justify-content-center min-vh-100 min-vw-100" style={{ background: "linear-gradient(135deg, #1e3c72, #2a5298)" }}>      
      <Card className="shadow-lg rounded-5 w-50 h-50 d-flex justify-content-center align-items-center">
        <Card.Body className="w-50 h-50">
          <div className="d-flex justify-content-end">
                <Button variant="link" href="/" className="p-0">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    className="bi bi-x"
                    viewBox="0 0 16 16"
                  >
                    <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708" />
                  </svg>
                </Button>
          </div>
          <div className="text-center mb-4">
              <Image
                src="path-to-logo" 
                alt="Logo"
                className="img-fluid"
                style={{ width: "80px", height: "80px" }}
              />
              <h2 className="card-title">{title}</h2>
              <p className="text-muted">
                {isLogin ? "Don't you have an account?" : "Already have an account?"} 
                <button 
                  className="btn-link text-primary" 
                  onClick={handleToggle} 
                  style={{ border: "none", background: "none", cursor: "pointer" }}
                >
                  {isLogin ? "Sign up" : "Log in"}
                </button>
              </p>
            </div>

          {isLogin ? <FormLogin /> : <FormRegister />}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default LoginRegisterPage;