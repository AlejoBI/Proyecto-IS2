import 'bootstrap/dist/css/bootstrap.min.css';

function NotFoundPage() {
  return (
    <div className="container mt-5 text-center">
      <h1 className="display-4">404 - Page Not Found</h1>
      <p className="lead">The page you are looking for does not exist.</p>
      <a href="/" className="btn btn-primary mt-3">Go to Homepage</a>
    </div>
  );
}
export default NotFoundPage;
