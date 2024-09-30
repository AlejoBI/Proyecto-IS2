import { useAuth } from "../context/AuthContext";
import { Form, Button, Container } from "react-bootstrap";

const FormRegister = () => {
  const { singup } = useAuth();

  const handleSubmit = (e) => {
    e.preventDefault();
    const username = e.target.username.value;
    const email = e.target.email.value;
    const password = e.target.password.value;
    const confirmPassword = e.target.confirmPassword.value;
    const role = "user";

    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    const data = { username, email, password, role };
    singup(data);
  };

  return (
    <Container className="p-4">
      <Form onSubmit={handleSubmit}>
        <Form.Group controlId="username" className="mb-3">
          <Form.Label>Username</Form.Label>
          <Form.Control
            type="text"
            placeholder="Enter username"
            name="username"
            required
          />
        </Form.Group>

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

        <Form.Group controlId="confirmPassword" className="mb-3">
          <Form.Label>Confirm Password</Form.Label>
          <Form.Control
            type="password"
            placeholder="Confirm password"
            name="confirmPassword"
            required
          />
        </Form.Group>

        <Button
          variant="success"
          type="submit"
          className="w-100"
          style={{ backgroundColor: "#007bff", borderColor: "#007bff" }}
        >
          Register
        </Button>
      </Form>
    </Container>
  );
};

export default FormRegister;