import {
  Container,
  Nav,
  Navbar,
  Button,
  Image,
  Dropdown,
} from "react-bootstrap";
import { useAuth } from "../context/AuthContext";
import Logo from "../assests/images/Logo.jpg";
import "../assests/css/Navbar.css";

const NavbarComponent = () => {
  const { isAuthenticated, logout, user } = useAuth();
  const tittle = user ? `${user.username}` : "Home";

  return (
    <Navbar
      style={{
        backgroundColor: "white",
        padding: "0.3% 8%",
      }}
      variant="dark"
      expand="lg"
    >
      <Container>
        <Navbar.Brand href="/">
          <div style={{ display: "flex", alignItems: "center" }}>
            <Image
              src={Logo}
              alt="Logo"
              height="70"
              className="d-inline-block align-top"
            />
          </div>
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="navbar-dark-example" />
        <Navbar.Collapse id="navbar-dark-example">
          <div
            style={{
              display: "flex",
              justifyContent: "flex-start",
              width: "100%",
              paddingLeft: "28%",
            }}
          ></div>
          <Nav style={{ justifyContent: "flex-end" }}>
            {isAuthenticated ? (
              <Dropdown>
                <Dropdown.Toggle variant="primary" id="dropdown-basic">
                  {tittle}
                </Dropdown.Toggle>

                <Dropdown.Menu>
                  {user && user.role === "user" && (
                    <>
                      <Dropdown.Item href="/user/profile">
                        Profile
                      </Dropdown.Item>
                      <Dropdown.Divider />
                    </>
                  )}
                  <Dropdown.Item onClick={logout}>Logout</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            ) : (
              <>
                <Button
                  href="/login"
                  style={{
                    backgroundColor: "#187A6B",
                    borderColor: "#187A6B",
                    marginRight: "10px",
                    fontWeight: "bold",
                  }}
                >
                  Login
                </Button>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default NavbarComponent;
