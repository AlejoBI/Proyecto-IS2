import FormLogin from "../components/FormLogin";
import FormRegister from "../components/FormRegister";
import { Card, Container, Image, Alert } from "react-bootstrap";
import { useEffect, useState } from "react";
import Logo from "../assests/images/Logo.jpg";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const LoginRegisterPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const { errors, setErrors } = useAuth();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleToggle = () => {
    setIsLogin((prevState) => !prevState);
  };

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated]);

  useEffect(() => {
    setErrors(null);
  }, [isLogin]);

  return (
    <Container
      className="d-flex align-items-center justify-content-center min-vh-100 min-vw-100"
      style={{ background: "#187A6B" }}
    >
      <Card className="shadow-lg rounded-5 w-50 h-50 d-flex justify-content-center align-items-center">
        <Card.Body className="w-50 h-50">
          <div className="text-center mb-4">
            <Link to="/">
              <Image
                src={Logo}
                alt="Logo"
                className="img-fluid"
                style={{ width: "80px", height: "80px" }}
              />
            </Link>
            <h2 className="card-title">{isLogin ? "Login" : "Register"}</h2>
            {errors && (
              <Alert variant="danger">
                {errors.detail ? errors.detail : errors}
              </Alert>
            )}{" "}
          </div>
          {isLogin ? <FormLogin /> : <FormRegister />}
          <p className="text-muted">
            {isLogin
              ? "Don't you have an account?"
              : "Already have an account?"}
            <button
              className="btn-link text-primary"
              onClick={handleToggle}
              style={{ border: "none", background: "none", cursor: "pointer" }}
            >
              {isLogin ? "Sign up" : "Log in"}
            </button>
          </p>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default LoginRegisterPage;
