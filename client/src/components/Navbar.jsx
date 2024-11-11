import { Container, Nav, Navbar, Button, Image, NavDropdown } from "react-bootstrap";
import "../assests/css/Navbar.css"; 
import { useAuth } from "../context/AuthContext";
import Logo from "../assests/images/Logo.jpg";

const NavbarComponent = () => {
  const { isAuthenticated, logout, user } = useAuth();
  const title = user ? `${user.username}` : "Home";

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
          >
          </div>
          <Nav style={{ justifyContent: "flex-end" }}>
            {isAuthenticated ? (
              <NavDropdown title={title} id="navbarScrollingDropdown">
                <NavDropdown.Item href="/user/profile">
                  Profile
                </NavDropdown.Item>
                <NavDropdown.Item
                  href="/"
                  onClick={() => {
                    logout();
                  }}
                >
                  Logout
                </NavDropdown.Item>
              </NavDropdown>
            ) : (
              <>
              <Button
                href="/login"
                style={{
                  backgroundColor: "#187A6B",
                  borderColor: "#187A6B",
                  marginRight: "10px",
                  fontWeight: "bold"                }}
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