import { useAuth } from "../context/AuthContext";
import { Form, Button, Container } from "react-bootstrap";

const FormLogin = () => {
  const { signin } = useAuth();

  const handleSubmit = (e) => {
    e.preventDefault();
    const email = e.target.email.value;
    const password = e.target.password.value;

    const data = { email, password };
    signin(data);
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

        <Button
          variant="primary"
          type="submit"
          className="w-100"
          style={{ backgroundColor: "#007bff", borderColor: "#007bff" }}        >
          Login
        </Button>
      </Form>
    </Container>
  );
};

export default FormLogin;